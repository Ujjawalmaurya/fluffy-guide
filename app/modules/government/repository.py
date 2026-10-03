"""
repository.py — Database operations for government monitoring and workforce statistics.
"""
from app.core.database import get_supabase


class GovernmentRepository:
    def __init__(self, db=None):
        self.db = db or get_supabase()

    def get_users_count(self) -> int:
        try:
            res = self.db.table("users").select("id", count="exact").execute()
            return res.count or 0
        except Exception:
            return 0

    def get_jobs_count(self) -> int:
        try:
            res = self.db.table("job_listings").select("id", count="exact").execute()
            return res.count or 0
        except Exception:
            return 0

    def get_resumes_analyzed_count(self) -> int:
        try:
            res = self.db.table("resume_analysis").select("id", count="exact").execute()
            return res.count or 0
        except Exception:
            return 0

    def get_youth_profiles(self, limit: int = 50) -> list:
        try:
            res = self.db.table("users").select("id, email, user_type, created_at").limit(limit).execute()
            return res.data or []
        except Exception:
            return []
