"""
Profile service — CRUD, resume parsing, profile completion scoring.
"""
from app.modules.profile.repository import ProfileRepository
from app.modules.profile.resume_parser import parse_resume
from app.modules.profile.schemas import ProfileUpdateIn
from app.shared.exceptions import ResumeInvalid, ResumeTooLarge
from app.core.logger import get_logger

log = get_logger("PROFILE")

MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5MB

# Fields that contribute to completion score
COMPLETION_FIELDS = ["full_name", "age", "gender", "state", "city", "education_level", "languages", "phone"]


class ProfileService:
    def __init__(self, repo: ProfileRepository):
        self.repo = repo

    def get_profile(self, user_id: str) -> dict:
        profile = self.repo.get_profile(user_id)
        return profile or {}

    def update_profile(self, user_id: str, data: ProfileUpdateIn) -> dict:
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

        from app.modules.ai_chat.providers.gemini import get_gemini_instance
        result = await parse_resume(file_bytes, filename, content_type, user_id, get_gemini_instance())

        self.repo.upsert_enrichment(
            user_id=user_id,
            original_name=filename,
            raw_text=result["raw_text"],
            parsed=result["parsed"],
        )

        # Merge parsed skills into user_skill_profiles — this feeds gap analysis
        parsed_skills = result["parsed"].get("skills", [])
        if parsed_skills:
            from app.modules.skill_profile import aggregator as skill_aggregator
            from app.modules.skill_profile.repository import SkillProfileRepository
            from app.core.database import get_supabase
            skill_repo = SkillProfileRepository(get_supabase())
            await skill_aggregator.merge_from_resume(user_id, parsed_skills, skill_repo)
            log.info(f"Skills merged into user_skill_profiles for user={user_id}. count={len(parsed_skills)}")
        else:
            log.warning(f"Resume parsed but no skills found for user={user_id}")

        log.info(f"Resume parsed for user={user_id}. Found {len(parsed_skills)} skills")

        return {
            "skills_found": parsed_skills,
            "education_hints": result["parsed"].get("education", []),
            "experience_hints": result["parsed"].get("experience", []),
            "experience_level": result["parsed"].get("experience_level"),
            "strengths": result["parsed"].get("strengths", []),
            "weaknesses": result["parsed"].get("weaknesses", []),
            "career_suggestions": result["parsed"].get("career_suggestions", []),
            "skill_gap_analysis": result["parsed"].get("skill_gap_analysis"),
        }

    def get_completion_score(self, user_id: str) -> dict:
        profile = self.repo.get_profile(user_id) or {}
        filled = [f for f in COMPLETION_FIELDS if profile.get(f)]
        missing = [f for f in COMPLETION_FIELDS if not profile.get(f)]
        score = int((len(filled) / len(COMPLETION_FIELDS)) * 100)
        log.debug(f"Computed profile_completion={score}% for user={user_id}")
        return {"score": score, "filled_fields": filled, "missing_fields": missing}
