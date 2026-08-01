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

def classify_user_type_from_resume(parsed_resume: dict) -> str | None:
    """Classifies user_type based on primary role and skills parsed from resume."""
    primary_role = str(parsed_resume.get("primary_role") or "").lower()
    skills = [str(s.get("name") or s).lower() for s in parsed_resume.get("skills", [])]
    summary = str(parsed_resume.get("summary") or "").lower()
    
    combined_text = f"{primary_role} {summary} " + " ".join(skills)
    
    # Keyword sets
    youth_kws = {
        "software", "developer", "engineer", "programmer", "coder", "analyst", "consultant", 
        "manager", "data", "designer", "administrator", "network", "system", "computer", "cse", 
        "it", "web", "frontend", "backend", "fullstack", "cloud", "aws", "digital", "marketing", 
        "sales", "finance", "accountant", "office", "hr", "recruiter", "project", "writer", 
        "editor", "teacher", "instructor", "academic", "student", "graduate", "college", 
        "university", "science", "technology", "information", "python", "java", "sql", "c++", 
        "javascript", "html", "css", "react", "node", "angular", "vue", "typescript", "git",
        "machine learning", "ai", "deep learning", "cybersecurity", "algorithms", "data structures",
        "intern", "artificial intelligence", "data science"
    }
    
    bluecollar_kws = {
        "mechanic", "driver", "technician", "plumber", "electrician", "welder", "painter", 
        "carpenter", "mason", "fitter", "machinist", "operator", "loader", "packer", "fabricator", 
        "automotive", "repair", "maintenance", "electric", "wiring", "welding", "plumbing", 
        "hvac", "rigging", "machinery"
    }
    
    informal_kws = {
        "delivery", "rider", "courier", "cashier", "waiter", "helper", "loader", "security guard", 
        "caretaker", "nanny", "tailor", "cook", "chef", "housekeeping", "cleaner", "salesperson", 
        "counter"
    }
    
    youth_score = sum(1 for kw in youth_kws if kw in combined_text)
    bluecollar_score = sum(1 for kw in bluecollar_kws if kw in combined_text)
    informal_score = sum(1 for kw in informal_kws if kw in combined_text)
    
    log.debug(f"[CLASSIFIER] Scores: youth={youth_score}, bluecollar={bluecollar_score}, informal={informal_score}")
    
    if youth_score == 0 and bluecollar_score == 0 and informal_score == 0:
        return None
        
    if youth_score >= bluecollar_score and youth_score >= informal_score:
        return "individual_youth"
    elif bluecollar_score >= youth_score and bluecollar_score >= informal_score:
        return "individual_bluecollar"
    else:
        return "individual_informal"

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

        # Determine user type and update users table if detected
        try:
            detected_type = classify_user_type_from_resume(result["parsed"])
            if detected_type:
                self.repo.db.table("users").update({"user_type": detected_type}).eq("id", user_id).execute()
                log.info(f"Updated user_type to {detected_type} for user={user_id} based on resume background")
        except Exception as e:
            log.error(f"Failed to auto-update user_type from resume for user={user_id}: {e}")

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

        # Update user_profiles and user_preferences tables with extracted interests/skills
        try:
            from app.core.database import get_supabase
            db = get_supabase()
            
            parsed_interests = result["parsed"].get("interests", [])
            primary_role = result["parsed"].get("primary_role")
            
            # 1. Update user_profiles
            profile_update = {}
            if parsed_interests:
                profile_update["interests"] = parsed_interests
            
            skill_names = [s.get("name") for s in cleaned_skills if s.get("name")]
            if skill_names:
                profile_update["secondary_skills"] = skill_names
                
            if profile_update:
                db.table("user_profiles").update(profile_update).eq("user_id", user_id).execute()
                log.info(f"Updated user_profiles for user={user_id} with: {profile_update}")
                
            # 2. Update/upsert user_preferences
            prefs_update = {}
            if parsed_interests:
                prefs_update["career_interests"] = parsed_interests
            if primary_role:
                prefs_update["target_roles"] = [primary_role]
                
            if prefs_update:
                db.table("user_preferences").upsert({"user_id": user_id, **prefs_update}, on_conflict="user_id").execute()
                log.info(f"Updated user_preferences for user={user_id} with: {prefs_update}")
                
        except Exception as db_err:
            log.error(f"Failed to update user_profiles/user_preferences after resume upload: {db_err}")

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
