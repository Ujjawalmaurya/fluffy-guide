"""
Profile service — CRUD, resume parsing, profile completion scoring.
"""
from app.modules.profile.repository import ProfileRepository
from app.modules.profile import resume_parser
from app.modules.profile.schemas import ProfileUpdateIn, BulletRewriteOut
from app.shared.exceptions import ResumeInvalid, ResumeTooLarge, RateLimitExceeded
from app.core.logger import get_logger
import asyncio

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

        from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
        from app.modules.ai_chat.providers.jev_provider import JevProvider

        ollama = get_ollama_instance()
        jev = JevProvider()

        # 1. Parsing with local high-context Ollama
        result = await resume_parser.parse_resume(file_bytes, filename, content_type, user_id, ollama)
        raw_text = result["raw_text"]

        # 2. Fast Deep Analysis
        ats_task = resume_parser.score_ats(raw_text, ollama)
        india_task = resume_parser.extract_india_details(raw_text, ollama)
        achievements_task = resume_parser.detect_achievements(raw_text, ollama)
        jev_flags_task = jev.evaluate_resume_ats_flags(raw_text)

        ats_res, india_res, achievements_res, jev_flags = await asyncio.gather(
            ats_task, india_task, achievements_task, jev_flags_task
        )
        ats_res.update(jev_flags)

        # 3. Store Enrichment
        full_parsed = {
            **result["parsed"],
            "ats_score": ats_res,
            "india_qualifications": india_res,
            "achievements": achievements_res.get("achievements", [])
        }

        self.repo.upsert_enrichment(
            user_id=user_id,
            original_name=filename,
            raw_text=raw_text,
            parsed=full_parsed,
        )

        # Merge parsed skills into user_skill_profiles
        parsed_skills = result["parsed"].get("skills", [])
        if parsed_skills:
            from app.modules.skill_profile import aggregator as skill_aggregator
            from app.modules.skill_profile.repository import SkillProfileRepository
            from app.core.database import get_supabase
            skill_repo = SkillProfileRepository(get_supabase())
            await skill_aggregator.merge_from_resume(user_id, parsed_skills, skill_repo)
            log.info(f"Skills merged for user={user_id}")

        return {
            "parser_result": result["parsed"],
            "india_qualifications": india_res,
            "achievements": achievements_res.get("achievements", []),
            "ats_score": ats_res,
            "suggestions": ats_res.get("suggestions", [])
        }

    async def rewrite_bullets(self, user_id: str, bullets: list[str]) -> BulletRewriteOut:
        # Rate limit: 5 per day
        limit = 5
        count = self.repo.get_daily_rewrite_count(user_id)
        if count >= limit:
            raise RateLimitExceeded(msg=f"Daily limit of {limit} reached.")

        from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
        ollama = get_ollama_instance()
        
        result = await resume_parser.rewrite_bullets(bullets, ollama)
        rewritten = result.get("rewritten_bullets", bullets)

        self.repo.increment_rewrite_count(user_id)
        
        return BulletRewriteOut(
            rewritten_bullets=rewritten,
            remaining_daily_rewrites=max(0, limit - (count + 1))
        )

    def get_completion_score(self, user_id: str) -> dict:
        profile = self.repo.get_profile(user_id) or {}
        filled = [f for f in COMPLETION_FIELDS if profile.get(f)]
        missing = [f for f in COMPLETION_FIELDS if not profile.get(f)]
        score = int((len(filled) / len(COMPLETION_FIELDS)) * 100)
        log.debug(f"Computed profile_completion={score}% for user={user_id}")
        return {"score": score, "filled_fields": filled, "missing_fields": missing}
