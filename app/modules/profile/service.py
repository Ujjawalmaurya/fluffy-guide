"""
Profile service — CRUD, resume parsing, profile completion scoring.
"""
from app.modules.profile.repository import ProfileRepository
from app.modules.profile.resume_parser import parse_resume
from app.schemas.request.profile import ProfileUpdateRequest
from app.shared.exceptions import ResumeInvalid, ResumeTooLarge
from app.core.logger import get_logger

log = get_logger("PROFILE")

MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5MB

# Fields that contribute to completion score
COMPLETION_FIELDS = ["full_name", "age", "gender", "state", "city", "education_level", "languages", "phone"]


from app.modules.ai_chat.providers.base import IStructuredProvider

class ProfileService:
    def __init__(self, repo: ProfileRepository, llm: IStructuredProvider):
        self.repo = repo
        self.llm = llm

    def get_profile(self, user_id: str) -> dict:
        profile = self.repo.get_profile(user_id)
        return profile or {}

    def update_profile(self, user_id: str, data: ProfileUpdateRequest) -> dict:
        self.repo.update_profile(user_id, data.model_dump(exclude_unset=True))
        return self.repo.get_profile(user_id) or {}

    async def upload_resume(self, user_id: str, filename: str, content_type: str, file_bytes: bytes) -> dict:
        allowed_types = (
            "application/pdf", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "application/octet-stream"
        )
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        
        if content_type not in allowed_types and ext not in ("pdf", "docx", "txt"):
            raise ResumeInvalid()
            
        if len(file_bytes) > MAX_RESUME_SIZE:
            raise ResumeTooLarge()

        # Ensure we have an enrichment record and it's set to 'processing'
        try:
            self.repo.update_enrichment_status(user_id, "processing")
        except Exception as e:
            log.warning(f"Could not set initial status to processing for user={user_id}: {e}")

        try:
            result = await parse_resume(file_bytes, filename, content_type, user_id, self.llm)
        except Exception as e:
            log.error(f"Resume parsing failed for user={user_id}: {e}")
            self.repo.update_enrichment_status(user_id, "failed")
            raise

        from app.core import llm_config
        try:
            self.repo.upsert_enrichment(
                user_id=user_id,
                original_name=filename,
                raw_text=result["raw_text"],
                parsed=result["parsed"],
                model=llm_config.RESUME_PARSE.model
            )
        except Exception as e:
            log.error(f"Failed to upsert enrichment for user={user_id}: {e}")
            # We don't raise here, we try to continue with skills merge

        # Merge parsed skills into user_skill_profiles
        parsed_skills = result["parsed"].get("skills", [])
        
        # Proficiency mapping: label to numeric
        prof_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Expert": 4}
        
        cleaned_skills = []
        for s in parsed_skills:
            # Ensure skill is a dict with name and proficiency
            if isinstance(s, str):
                s = {"name": s, "category": "technical", "proficiency": "Intermediate"}
            
            label = s.get("proficiency", "Intermediate")
            s["proficiency_numeric"] = prof_map.get(label, 2)
            s["proficiency_label"] = label
            # Add confidence if missing
            if "confidence" not in s:
                s["confidence"] = 0.8 # Default confidence for resume extraction
            cleaned_skills.append(s)

        if cleaned_skills:
            try:
                from app.modules.skill_profile import aggregator as skill_aggregator
                from app.modules.skill_profile.repository import SkillProfileRepository
                from app.core.database import get_supabase
                skill_repo = SkillProfileRepository(get_supabase())
                await skill_aggregator.merge_from_resume(user_id, cleaned_skills, skill_repo)
                log.info(f"Skills merged into user_skill_profiles for user={user_id}. count={len(cleaned_skills)}")
            except Exception as e:
                log.error(f"Failed to merge skills for user={user_id}: {e}")
        else:
            log.warning(f"Resume parsed but no skills found for user={user_id}")

        log.info(f"Resume parsed for user={user_id}. Found {len(cleaned_skills)} skills")
        self.repo.log_activity(
            user_id, 
            "resume_upload", 
            f"Uploaded resume: {filename}",
            {"skills_count": len(cleaned_skills), "primary_role": result["parsed"].get("primary_role")}
        )

        return {
            "skills_found": cleaned_skills,
            "education_hints": result["parsed"].get("education", []),
            "experience_hints": result["parsed"].get("experience", []),
            "primary_role": result["parsed"].get("primary_role"),
            "total_experience_years": result["parsed"].get("total_experience_years"),
            "summary": result["parsed"].get("summary"),
            "strengths": result["parsed"].get("strengths", []),
            "weaknesses": result["parsed"].get("weaknesses", []),
            "career_suggestions": result["parsed"].get("career_suggestions", []),
            "skill_gap_analysis": result["parsed"].get("skill_gap_analysis"),
            "status": "done"
        }


    def get_completion_score(self, user_id: str) -> dict:
        profile = self.repo.get_profile(user_id) or {}
        filled = [f for f in COMPLETION_FIELDS if profile.get(f)]
        missing = [f for f in COMPLETION_FIELDS if not profile.get(f)]
        score = int((len(filled) / len(COMPLETION_FIELDS)) * 100)
        log.debug(f"Computed profile_completion={score}% for user={user_id}")
        return {"score": score, "filled_fields": filled, "missing_fields": missing}
