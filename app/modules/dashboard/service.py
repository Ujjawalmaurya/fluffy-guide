"""Dashboard service — aggregates data from multiple tables into a single summary."""
from app.modules.dashboard.repository import DashboardRepository
from app.core.logger import get_logger

log = get_logger("DASHBOARD")

# Fields that count toward profile completion
PROFILE_FIELDS = ["full_name", "age", "gender", "state", "city", "education_level", "languages", "phone"]


class DashboardService:
    def __init__(self, repo: DashboardRepository):
        self.repo = repo

    def get_summary(self, user_id: str) -> dict:
        user = self.repo.get_user(user_id) or {}
        profile = self.repo.get_profile(user_id) or {}
        prefs = self.repo.get_preferences(user_id) or {}
        session = self.repo.get_latest_session(user_id) or {}

        # Profile completion
        filled = [f for f in PROFILE_FIELDS if profile.get(f)]
        completion_pct = int(len(filled) / len(PROFILE_FIELDS) * 100)

        state = profile.get("state", "")
        career_interests = prefs.get("career_interests", [])
        extracted_skills = session.get("extracted_skills") or []

        job_matches = self.repo.get_job_matches(state, career_interests)

        log.debug(f"Computed profile_completion={completion_pct}% for user={user_id}")

        return {
            "user": {
                "name": profile.get("full_name", user.get("email", "")),
                "user_type": user.get("user_type"),
                "preferred_lang": user.get("preferred_lang", "en"),
            },
            "profile_completion_pct": completion_pct,
            "onboarding_done": user.get("onboarding_done", False),
            "quick_assessment_done": False,  # feature stub in MVP
            "gap_analysis_done": False,       # feature stub in MVP
            "extracted_skills": extracted_skills,
            "career_interests": career_interests,
            "location": {"state": profile.get("state"), "city": profile.get("city")},
            "job_matches": job_matches,
        }
