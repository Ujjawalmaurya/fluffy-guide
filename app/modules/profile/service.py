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

    def upload_resume(self, user_id: str, filename: str, content_type: str, file_bytes: bytes) -> dict:
        if content_type not in ("application/pdf", "application/octet-stream") and not filename.lower().endswith(".pdf"):
            raise ResumeInvalid()
        if len(file_bytes) > MAX_RESUME_SIZE:
            raise ResumeTooLarge()

        result = parse_resume(file_bytes, filename)
        self.repo.upsert_enrichment(
            user_id=user_id,
            original_name=filename,
            raw_text=result["raw_text"],
            parsed=result["parsed"],
        )
        log.info(f"Resume parsed for user={user_id}. Found {len(result['parsed']['skills'])} skills: {result['parsed']['skills'][:5]}")
        return {
            "skills_found": result["parsed"]["skills"],
            "education_hints": result["parsed"]["education"],
            "experience_hints": result["parsed"]["experience"],
        }

    def get_completion_score(self, user_id: str) -> dict:
        profile = self.repo.get_profile(user_id) or {}
        filled = [f for f in COMPLETION_FIELDS if profile.get(f)]
        missing = [f for f in COMPLETION_FIELDS if not profile.get(f)]
        score = int((len(filled) / len(COMPLETION_FIELDS)) * 100)
        log.debug(f"Computed profile_completion={score}% for user={user_id}")
        return {"score": score, "filled_fields": filled, "missing_fields": missing}
