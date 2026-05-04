"""Dashboard repository — joins across profile, preferences, questionnaire, and jobs tables."""
from supabase import Client
from app.core.logger import get_logger

log = get_logger("DASHBOARD")


class DashboardRepository:
    def __init__(self, db: Client):
        self.db = db

    async def get_user(self, user_id: str) -> dict | None:
        result = self.db.table("users").select("*").eq("id", user_id).single().execute()
        return result.data

    async def get_profile(self, user_id: str) -> dict | None:
        result = self.db.table("user_profiles").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    async def get_preferences(self, user_id: str) -> dict | None:
        result = self.db.table("user_preferences").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    async def get_latest_session(self, user_id: str) -> dict | None:
        result = self.db.table("questionnaire_sessions") \
            .select("extracted_skills") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None

    async def get_job_matches(self, state: str, interests: list[str], user_skills: list[str] = None, limit: int = 3) -> list[dict]:
        user_skills = user_skills or []
        user_skills_set = {s.lower() for s in user_skills}
        
        # Increase fetch limit to rank a better pool
        query = self.db.table("job_listings") \
            .select("id,title,company,location_city,category,required_skills,salary_min,salary_max") \
            .eq("is_active", True)

        if state:
            query = query.eq("location_state", state)

        result = query.limit(20).execute()
        if not result.data:
            return []

        scored_jobs = []
        for job in result.data:
            score = 0
            title_lower = job.get("title", "").lower()
            job_category = job.get("category", "").lower()
            job_skills = [s.lower() for s in (job.get("required_skills") or [])]
            
            # 1. Category Match (Strong signal)
            if job_category in [i.lower() for i in interests]:
                score += 50
            
            # 2. Skill Overlap (The missing "beat")
            # For each user skill found in job's required skills
            overlap = set(job_skills).intersection(user_skills_set)
            score += len(overlap) * 15  # 15 points per matching skill
            
            # 3. Title Keyword Match
            # If a user's skill appears in the job title (e.g. "Flutter" in "Senior Flutter Developer")
            for skill in user_skills_set:
                if skill in title_lower:
                    score += 25
            
            # Add to list with score
            job["match_score"] = score
            scored_jobs.append(job)

        # Sort by score descending
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        log.info(f"Job matching for skills={user_skills[:3]}...: top_score={scored_jobs[0]['match_score'] if scored_jobs else 0}")
        
        return scored_jobs[:limit]
    async def get_government_schemes(self, state: str = None) -> list[dict]:
        query = self.db.table("government_schemes").select("*").eq("is_active", True)
        if state:
            # Simple check for now, later can use eligibility JSON
            pass
        return query.limit(3).execute().data

    async def get_competitive_exams(self, education_level: str = None) -> list[dict]:
        query = self.db.table("competitive_exams").select("*").eq("is_active", True)
        if education_level:
            query = query.eq("education_level", education_level)
        return query.limit(3).execute().data

    async def get_trade_market_data(self, trade_name: str, state: str) -> dict | None:
        result = self.db.table("trade_market_data") \
            .select("*") \
            .eq("trade_name", trade_name) \
            .eq("state", state) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None

    async def get_recommended_resources(self, skill_tags: list[str], limit: int = 3) -> list[dict]:
        if not skill_tags:
            return self.db.table("learning_resources").select("*").limit(limit).execute().data
        
        # Simple overlap check via GIN index would be better, but for now:
        result = self.db.table("learning_resources") \
            .select("*") \
            .contains("skill_tags", skill_tags[:3]) \
            .limit(limit) \
            .execute()
        return result.data

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
            log.error(f"Failed to log activity {activity_type} for user={user_id}: {e}")

    async def get_recent_activities(self, user_id: str, limit: int = 5) -> list[dict]:
        """Fetches the most recent activities for a user."""
        try:
            result = self.db.table("user_activities") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return result.data
        except Exception as e:
            log.error(f"Failed to fetch activities for user={user_id}: {e}")
            return []
