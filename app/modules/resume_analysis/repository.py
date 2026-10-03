"""
repository.py — Database persistence and skill-sync operations for resume analysis.
"""
from typing import Optional, Dict, Any, List
from loguru import logger
from app.core.database import get_supabase
from app.modules.resume_analysis.schemas import ResumeAnalysisResult, StructuredProfile


class ResumeAnalysisRepository:
    def __init__(self, db=None):
        self.db = db or get_supabase()

    def upsert_analysis(self, user_id: str, result: ResumeAnalysisResult, effective_roles: List[str]) -> bool:
        """Upserts full analysis result to the resume_analysis table."""
        try:
            db_data = {
                "user_id": user_id,
                "structured_profile": result.structured_profile.model_dump(),
                "quality_scores": result.quality_scores.model_dump(),
                "suggestions": result.suggestions.model_dump(),
                "india_flags": result.suggestions.india_specific_flags,
                "raw_text": result.raw_text,
                "overall_score": result.quality_scores.overall,
                "target_roles": effective_roles,
                "updated_at": "now()",
            }
            self.db.table("resume_analysis").upsert(db_data).execute()
            logger.info(f"[RESUME_REPO] Analysis upserted for user={user_id}")
            return True
        except Exception as e:
            logger.error(f"[RESUME_REPO] Database persistence failed: {e}")
            return False

    def get_latest_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Returns the latest resume analysis record for a user."""
        res = (
            self.db.table("resume_analysis")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def get_score_breakdown(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Returns score metrics and flags for quick dashboard viewing."""
        res = (
            self.db.table("resume_analysis")
            .select("quality_scores, overall_score, india_flags")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    async def sync_skills_to_profile(self, user_id: str, profile: StructuredProfile):
        """Auto-syncs extracted skills to user_skill_profiles via skill aggregator."""
        if not profile.skills:
            return

        try:
            from app.modules.skill_profile import aggregator as skill_aggregator
            from app.modules.skill_profile.repository import SkillProfileRepository

            skill_repo = SkillProfileRepository(self.db)
            parsed_skills = [
                {
                    "name": s.name,
                    "proficiency_label": s.level or "intermediate",
                    "category": "technical",
                    "confidence_score": 0.95,
                }
                for s in profile.skills
            ]
            await skill_aggregator.merge_from_resume(user_id, parsed_skills, skill_repo)
            logger.info(f"[RESUME_REPO] Synced {len(parsed_skills)} skills to user={user_id}")
        except Exception as e:
            logger.error(f"[RESUME_REPO] Skill sync failed: {e}")
