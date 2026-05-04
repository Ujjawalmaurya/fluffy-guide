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
        """Update user_profiles with filtered data."""
        profile_cols = {
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
        
        # Map languages_known if present
        if "languages_known" in profile_data:
            profile_data["languages"] = profile_data.pop("languages_known")

        # Map NGO fields
        if "org_name" in profile_data:
            profile_data["company_name"] = profile_data.pop("org_name")
        if "contact_name" in profile_data:
            profile_data["full_name"] = profile_data.pop("contact_name")
            
        # Map Employer fields
        if "contact_person_name" in profile_data and not profile_data.get("full_name"):
            profile_data["full_name"] = profile_data.get("contact_person_name")

        filtered_data = {k: v for k, v in profile_data.items() if k in profile_cols}
        return self.db.table("user_profiles").upsert(
            {"user_id": user_id, **filtered_data}, on_conflict="user_id"
        ).execute()

    async def save_blue_collar_profile(self, user_id: str, profile_data: dict):
        return await self.save_user_profile(user_id, profile_data)

    async def save_informal_worker_profile(self, user_id: str, profile_data: dict):
        # The table 'informal_worker_profiles' does not exist in schema, redirecting to user_profiles
        return await self.save_user_profile(user_id, profile_data)

    async def save_employer_profile(self, user_id: str, profile_data: dict):
        # The table 'employer_profiles' does not exist in schema, redirecting to user_profiles
        return await self.save_user_profile(user_id, profile_data)

    async def save_ngo_profile(self, user_id: str, profile_data: dict):
        return await self.save_user_profile(user_id, profile_data)

    async def save_govt_profile(self, user_id: str, profile_data: dict):
        return await self.save_user_profile(user_id, profile_data)

    async def update_user_onboarding_status(self, user_id: str, update_data: dict):
        return self.db.table("users").update(update_data).eq("id", user_id).execute()

    # ── Step 3: Preferences ───────────────────────────────────

    async def upsert_profile(self, user_id: str, data: dict):
        return self.db.table("user_profiles").upsert({"user_id": user_id, **data}, on_conflict="user_id").execute()

    async def upsert_preferences(self, user_id: str, data: dict):
        return self.db.table("user_preferences").upsert({"user_id": user_id, **data}, on_conflict="user_id").execute()

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
        
        # Update onboarding_state table if it exists for this user
        return self.db.table("onboarding_state").upsert({
            "user_id": user_id,
            "current_step": 5, # Representing completion
            "completed_steps": [1, 2, 3, 4]
        }, on_conflict="user_id").execute()

    async def update_user_onboarding(self, user_id: str, step: int, percentage: int):
        # onboarding_step and profile_complete_percentage don't exist in 'users' table.
        # We use onboarding_state table instead.
        return self.db.table("onboarding_state").upsert({
            "user_id": user_id,
            "current_step": step,
        }, on_conflict="user_id").execute()

    async def save_student_profile(self, user_id: str, profile_data: dict):
        """Update user_profiles and user_preferences with student data."""
        # 1. Save Profile Data
        await self.save_user_profile(user_id, profile_data)

        # 2. Save Preference Data
        pref_cols = {
            "career_interests", "expected_salary_min", "expected_salary_max", 
            "work_type", "willing_to_relocate", "target_roles"
        }
        
        # Map preferred_job_location to work_type if present
        if "preferred_job_location" in profile_data:
            profile_data["work_type"] = profile_data.pop("preferred_job_location")

        filtered_prefs = {k: v for k, v in profile_data.items() if k in pref_cols}
        if filtered_prefs:
            return self.db.table("user_preferences").upsert({
                "user_id": user_id,
                **filtered_prefs
            }, on_conflict="user_id").execute()

    def get_jobs_for_state(self, state: str, limit: int = 10) -> list[dict]:
        result = self.db.table("job_listings") \
            .select("*") \
            .eq("location_state", state) \
            .eq("is_active", True) \
            .limit(limit) \
            .execute()
        return result.data or []

    async def save_employer_profile(self, user_id: str, profile_data: dict):
        return await self.save_user_profile(user_id, profile_data)

    async def save_ngo_profile(self, user_id: str, profile_data: dict):
        return await self.save_user_profile(user_id, profile_data)

    async def save_govt_profile(self, user_id: str, profile_data: dict):
        return await self.save_user_profile(user_id, profile_data)
