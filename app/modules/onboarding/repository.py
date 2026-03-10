"""
Onboarding repository — all DB queries for onboarding tables.
Handles: users, user_profiles, user_preferences, onboarding_state, questionnaire_sessions.
"""
from supabase import Client
from app.core.logger import get_logger

log = get_logger("ONBOARDING")


class OnboardingRepository:
    def __init__(self, db: Client):
        self.db = db

    # ── Onboarding State ──────────────────────────────────────

    def get_state(self, user_id: str) -> dict | None:
        result = self.db.table("onboarding_state").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    def upsert_state(self, user_id: str, current_step: int, completed_steps: list[int], step_data: dict = None):
        self.db.table("onboarding_state").upsert({
            "user_id": user_id,
            "current_step": current_step,
            "completed_steps": completed_steps,
            "step_data": step_data or {},
        }, on_conflict="user_id").execute()

    # ── Step 1: User Type ─────────────────────────────────────

    def set_user_type(self, user_id: str, user_type: str):
        self.db.table("users").update({"user_type": user_type}).eq("id", user_id).execute()

    def get_user(self, user_id: str) -> dict | None:
        result = self.db.table("users").select("*").eq("id", user_id).single().execute()
        return result.data

    # ── Step 2: Profile ───────────────────────────────────────

    def upsert_profile(self, user_id: str, data: dict):
        self.db.table("user_profiles").upsert({"user_id": user_id, **data}, on_conflict="user_id").execute()

    # ── Step 3: Preferences ───────────────────────────────────

    def upsert_preferences(self, user_id: str, data: dict):
        self.db.table("user_preferences").upsert({"user_id": user_id, **data}, on_conflict="user_id").execute()

    def get_preferences(self, user_id: str) -> dict | None:
        result = self.db.table("user_preferences").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    # ── Step 4/5: Questionnaire ───────────────────────────────

    def create_questionnaire_session(self, user_id: str, language: str, questions_data: list) -> dict:
        result = self.db.table("questionnaire_sessions").insert({
            "user_id": user_id,
            "language": language,
            "questions_data": questions_data,
        }).execute()
        return result.data[0]

    def get_questionnaire_session(self, session_id: str) -> dict | None:
        result = self.db.table("questionnaire_sessions").select("*").eq("id", session_id).single().execute()
        return result.data

    def get_latest_session(self, user_id: str) -> dict | None:
        result = self.db.table("questionnaire_sessions") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None

    def submit_answers(self, session_id: str, answers_data: list):
        from datetime import datetime, timezone
        self.db.table("questionnaire_sessions").update({
            "answers_data": answers_data,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", session_id).execute()

    def save_extracted_skills(self, session_id: str, skills: list[str]):
        self.db.table("questionnaire_sessions").update({
            "extracted_skills": skills,
        }).eq("id", session_id).execute()

    def mark_onboarding_done(self, user_id: str):
        self.db.table("users").update({"onboarding_done": True}).eq("id", user_id).execute()

    def get_jobs_for_state(self, state: str, limit: int = 10) -> list[dict]:
        result = self.db.table("job_listings") \
            .select("*") \
            .eq("location_state", state) \
            .eq("is_active", True) \
            .limit(limit) \
            .execute()
        return result.data or []
