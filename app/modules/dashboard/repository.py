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

    def get_job_matches(self, state: str, interests: list[str], user_skills: list[str] = None, limit: int = 3) -> list[dict]:
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
