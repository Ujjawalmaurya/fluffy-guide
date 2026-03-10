"""Dashboard repository — joins across profile, preferences, questionnaire, and jobs tables."""
from supabase import Client
from app.core.logger import get_logger

log = get_logger("DASHBOARD")


class DashboardRepository:
    def __init__(self, db: Client):
        self.db = db

    def get_user(self, user_id: str) -> dict | None:
        result = self.db.table("users").select("*").eq("id", user_id).single().execute()
        return result.data

    def get_profile(self, user_id: str) -> dict | None:
        result = self.db.table("user_profiles").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    def get_preferences(self, user_id: str) -> dict | None:
        result = self.db.table("user_preferences").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    def get_latest_session(self, user_id: str) -> dict | None:
        result = self.db.table("questionnaire_sessions") \
            .select("extracted_skills") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None

    def get_job_matches(self, state: str, interests: list[str], limit: int = 3) -> list[dict]:
        query = self.db.table("job_listings") \
            .select("id,title,company,location_city,salary_min,salary_max,required_skills") \
            .eq("is_active", True)

        if state:
            query = query.eq("location_state", state)

        result = query.limit(limit * 3).execute()  # get more, filter for overlap

        if not result.data:
            return []

        # Prefer jobs that match interests/categories
        matched = [j for j in result.data if j.get("category") in interests]
        unmatched = [j for j in result.data if j not in matched]
        return (matched + unmatched)[:limit]
