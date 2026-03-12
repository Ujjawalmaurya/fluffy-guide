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

        # Fetch skills from user_skill_profiles instead of session
        db = self.repo.db # Using raw supabase client since we need to directly hit tables the repo doesn't map yet
        skills_result = db.table("user_skill_profiles").select(
           "skills"
        ).eq("user_id", user_id).limit(1).execute()
        extracted_skills = [
           s["skill_name"]
           for s in (skills_result.data[0]["skills"]
                     if skills_result.data and skills_result.data[0].get("skills") else [])
        ]

        # Check if assessment is done
        user_row = db.table("users").select(
           "quick_assessment_done"
        ).eq("id", user_id).limit(1).execute()
        assessment_done = (
           user_row.data[0].get("quick_assessment_done", False)
           if user_row.data else False
        )

        # Check gap analysis report status
        gap_row = db.table("gap_analysis_reports").select(
           "is_stale, computed_at, gaps"
        ).eq("user_id", user_id).limit(1).execute()
        gap_report = gap_row.data[0] if gap_row.data else None
        top_2_gaps = (
           gap_report["gaps"][:2] if gap_report and gap_report.get("gaps") else []
        )

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
            "quick_assessment_done": assessment_done,
            "assessment_status": {
                "has_completed": assessment_done,
            },
            "gap_analysis_done": gap_report is not None,
            "gap_analysis_status": {
                "has_report": gap_report is not None,
                "is_stale": gap_report["is_stale"] if gap_report else False,
                "top_2_gaps": top_2_gaps
            },
            "extracted_skills": extracted_skills,
            "career_interests": career_interests,
            "location": {"state": profile.get("state"), "city": profile.get("city")},
            "job_matches": job_matches,
        }
