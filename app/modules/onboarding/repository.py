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

    PROFILE_COLUMNS = {
        "full_name", "age", "gender", "state", "city", 
        "education_level", "languages", "phone", "avatar_url", 
        "career_identity", "stream", "institution_name", "primary_trade",
        "secondary_skills", "years_experience", "is_currently_employed",
        "preferred_work_radius", "owns_smartphone", "current_work_type",
        "monthly_income", "digital_literacy", "interests", "designation",
        "company_name", "industry_sector", "company_size", "roles_hiring_for",
        "preferred_skills", "work_type_offered", "registration_number",
        "focus_sectors", "coverage_areas", "beneficiary_types",
        "department", "access_level", "state_jurisdiction", "district_jurisdiction",
        "preferred_job_location", "village_district", "city_village",
        "contact_person_name", "contact_designation"
    }

    PREFERENCE_COLUMNS = {
        "career_interests", "expected_salary_min", "expected_salary_max", 
        "work_type", "willing_to_relocate", "target_roles"
    }

    FIELD_MAPPINGS = {
        "languages_known": "languages",
        "org_name": "company_name",
        "contact_name": "full_name",
        "contact_person_name": "full_name",
        "college_name": "institution_name",
        "reg_number": "registration_number",
        "industry": "industry_sector",
        "hiring_roles": "roles_hiring_for",
        "candidate_skills": "preferred_skills"
    }

    # ── Onboarding State ──────────────────────────────────────

    async def get_state(self, user_id: str) -> dict | None:
        result = self.db.table("onboarding_state").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    async def upsert_state(self, user_id: str, current_step: int, completed_steps: list[int], step_data: dict = None):
        return self.db.table("onboarding_state").upsert({
            "user_id": user_id,
            "current_step": current_step,
            "completed_steps": completed_steps,
            "step_data": step_data or {},
        }, on_conflict="user_id").execute()

    # ── Step 1: User Type ─────────────────────────────────────

    async def set_user_type(self, user_id: str, user_type: str):
        return self.db.table("users").update({"user_type": user_type}).eq("id", user_id).execute()

    async def get_user(self, user_id: str) -> dict | None:
        result = self.db.table("users").select("*").eq("id", user_id).single().execute()
        return result.data

    async def save_user_profile(self, user_id: str, profile_data: dict):
        """Update user_profiles and user_preferences with filtered and mapped data."""
        data = profile_data.copy()
        
        # Apply mappings
        for source, target in self.FIELD_MAPPINGS.items():
            if source in data:
                if not data.get(target):
                    data[target] = data.get(source)
                data.pop(source, None)

        # Mapping preferred_job_location to work_type for backwards compatibility
        if "preferred_job_location" in data and not data.get("work_type"):
            data["work_type"] = data["preferred_job_location"]

        filtered_profile = {k: v for k, v in data.items() if k in self.PROFILE_COLUMNS and v is not None}
        filtered_prefs = {k: v for k, v in data.items() if k in self.PREFERENCE_COLUMNS and v is not None}
        
        # Upsert Profile
        res = self.db.table("user_profiles").upsert(
            {"user_id": user_id, **filtered_profile}, on_conflict="user_id"
        ).execute()

        # Upsert Preferences if data exists
        if filtered_prefs:
            self.db.table("user_preferences").upsert(
                {"user_id": user_id, **filtered_prefs}, on_conflict="user_id"
            ).execute()

        return res

    async def update_user_onboarding_status(self, user_id: str, update_data: dict):
        return self.db.table("users").update(update_data).eq("id", user_id).execute()

    # ── Step 3: Preferences ───────────────────────────────────

    async def get_preferences(self, user_id: str) -> dict | None:
        result = self.db.table("user_preferences").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    # ── Step 4/5: Questionnaire ───────────────────────────────

    async def create_questionnaire_session(self, user_id: str, language: str, questions_data: list) -> dict:
        result = self.db.table("questionnaire_sessions").insert({
            "user_id": user_id,
            "language": language,
            "questions_data": questions_data,
        }).execute()
        return result.data[0]

    async def get_questionnaire_session(self, session_id: str) -> dict | None:
        result = self.db.table("questionnaire_sessions").select("*").eq("id", session_id).single().execute()
        return result.data

    async def get_latest_session(self, user_id: str) -> dict | None:
        result = self.db.table("questionnaire_sessions") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None

    async def submit_answers(self, session_id: str, answers_data: list):
        from datetime import datetime, timezone
        return self.db.table("questionnaire_sessions").update({
            "answers_data": answers_data,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", session_id).execute()

    async def save_extracted_skills(self, session_id: str, skills: list[str]):
        return self.db.table("questionnaire_sessions").update({
            "extracted_skills": skills,
        }).eq("id", session_id).execute()

    async def mark_onboarding_done(self, user_id: str):
        # Update users table
        self.db.table("users").update({
            "onboarding_done": True
        }).eq("id", user_id).execute()
        
        # Update onboarding_state table
        return self.db.table("onboarding_state").upsert({
            "user_id": user_id,
            "current_step": 5,
            "completed_steps": [1, 2, 3, 4]
        }, on_conflict="user_id").execute()

    async def update_user_onboarding(self, user_id: str, step: int, percentage: int):
        return self.db.table("onboarding_state").upsert({
            "user_id": user_id,
            "current_step": step,
            "completed_steps": list(range(1, step))
        }, on_conflict="user_id").execute()

    def get_jobs_for_state(self, state: str, limit: int = 10) -> list[dict]:
        result = self.db.table("job_listings") \
            .select("*") \
            .eq("location_state", state) \
            .eq("is_active", True) \
            .limit(limit) \
            .execute()
        return result.data or []
