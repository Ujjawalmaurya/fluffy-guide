"""
service.py — Business logic and metric aggregation for government officer portal.
"""
from typing import Dict, Any, List
from app.modules.government.repository import GovernmentRepository


class GovernmentService:
    def __init__(self, repo: GovernmentRepository):
        self.repo = repo

    def get_global_stats(self) -> Dict[str, Any]:
        """Calculates global workforce and scheme metrics."""
        users_count = self.repo.get_users_count()
        jobs_count = self.repo.get_jobs_count()
        resumes_count = self.repo.get_resumes_analyzed_count()

        return {
            "total_youth_registered": users_count,
            "total_jobs_available": jobs_count,
            "total_assessments_completed": resumes_count,
            "active_programs": 12,
            "placement_rate": "68%",
        }

    def get_youth_list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns registered youth profiles for scheme monitoring."""
        return self.repo.get_youth_profiles(limit=limit)
