from typing import Optional
from supabase import Client
from app.core.logger import get_logger

logger = get_logger("ASSESSMENT")


class AssessmentRepository:
    def __init__(self, db: Client):
        self.db = db

    async def create_session(self, user_id: str, retake_number: int, max_retakes: int) -> dict:
        """Creates a new questionnaire_sessions record for quick_assessment."""
        result = self.db.table("questionnaire_sessions").insert({
            "user_id": user_id,
            "assessment_type": "quick_assessment",
            "retake_number": retake_number,
            "max_retakes": max_retakes,
            "phase": 1,
            "current_question_number": 0,
            "adaptive_context": [],
            "extracted_proficiency": [],
            "is_complete": False,
            "language": "en"
        }).execute()
        logger.debug(f"[ASSESSMENT] Session created. user={user_id}. retake={retake_number}")
        return result.data[0]

    async def get_active_session(self, user_id: str) -> dict | None:
        """Returns the most recent INCOMPLETE quick_assessment session."""
        result = (
            self.db.table("questionnaire_sessions")
            .select("*")
            .eq("user_id", user_id)
            .eq("assessment_type", "quick_assessment")
            .eq("is_complete", False)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    async def delete_active_session(self, user_id: str) -> bool:
        """Deletes the active/incomplete quick_assessment session for the user."""
        self.db.table("questionnaire_sessions").delete().eq("user_id", user_id).eq("assessment_type", "quick_assessment").eq("is_complete", False).execute()
        return True

    async def get_session_by_id(self, session_id: str, user_id: str) -> dict | None:
        """Fetches a session by ID with ownership check."""
        result = (
            self.db.table("questionnaire_sessions")
            .select("*")
            .eq("id", session_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    async def update_session(self, session_id: str, **fields) -> dict:
        """Updates any subset of fields on a session record."""
        result = (
            self.db.table("questionnaire_sessions")
            .update(fields)
            .eq("id", session_id)
            .execute()
        )
        return result.data[0]

    async def get_completed_count(self, user_id: str) -> int:
        """Returns count of completed quick_assessment sessions."""
        result = (
            self.db.table("questionnaire_sessions")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("assessment_type", "quick_assessment")
            .eq("is_complete", True)
            .execute()
        )
        return result.count or 0

    async def get_last_completed(self, user_id: str) -> dict | None:
        """Returns the most recently completed quick_assessment session."""
        result = (
            self.db.table("questionnaire_sessions")
            .select("*")
            .eq("user_id", user_id)
            .eq("assessment_type", "quick_assessment")
            .eq("is_complete", True)
            .order("completed_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    async def get_history(self, user_id: str) -> list:
        """Returns all quick_assessment sessions for a user, newest first."""
        result = (
            self.db.table("questionnaire_sessions")
            .select(
                "id, retake_number, is_complete, completed_at, "
                "extracted_proficiency, current_question_number, created_at"
            )
            .eq("user_id", user_id)
            .eq("assessment_type", "quick_assessment")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    async def log_activity(self, user_id: str, activity_type: str, description: str, metadata: dict = None):
        """Logs a user activity to the database."""
        try:
            self.db.table("user_activities").insert({
                "user_id": user_id,
                "activity_type": activity_type,
                "description": description,
                "metadata": metadata or {}
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log activity {activity_type} for user={user_id}: {e}")

    async def mark_assessment_done(self, user_id: str):
        """Marks the quick assessment as done in the users table."""
        return self.db.table("users").update({"quick_assessment_done": True}).eq("id", user_id).execute()

    async def get_last_completed_at(self, user_id: str) -> Optional[str]:
        """Gets the timestamp of the last completed assessment."""
        res = self.db.table("questionnaire_sessions").select("completed_at").eq("user_id", user_id).eq("is_complete", True).order("completed_at", desc=True).limit(1).execute()
        return res.data[0]["completed_at"] if res.data else None

    async def invalidate_gap_analysis(self, user_id: str):
        """Marks gap analysis reports as stale."""
        return self.db.table("gap_analysis_reports").update({"is_stale": True}).eq("user_id", user_id).execute()

    async def get_user_profile_and_prefs(self, user_id: str) -> dict:
        """Fetches profile, preferences, user info, and resume enrichment."""
        user = self.db.table("users").select("*").eq("id", user_id).limit(1).execute()
        profile = self.db.table("user_profiles").select("*").eq("user_id", user_id).limit(1).execute()
        prefs = self.db.table("user_preferences").select("*").eq("user_id", user_id).limit(1).execute()
        enrichment = self.db.table("profile_enrichments").select("*").eq("user_id", user_id).limit(1).execute()
        return {
            "user": user.data[0] if user.data else {},
            "profile": profile.data[0] if profile.data else {},
            "preferences": prefs.data[0] if prefs.data else {},
            "enrichment": enrichment.data[0] if enrichment.data else {}
        }