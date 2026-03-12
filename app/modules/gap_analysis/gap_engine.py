# [GAP_ANALYSIS] Core gap computation — no LLM calls here.
# Pure data: compares user skills against job market requirements.

from app.core.database import get_supabase
from app.core.logger import get_logger
from app.shared.exceptions import AppError

logger = get_logger("GAP_ANALYSIS")

class GAP_ANALYSIS_NO_SKILLS(AppError):
    def __init__(self):
        super().__init__("GAP_ANALYSIS_NO_SKILLS", "You need to add some skills or take an assessment first.", 400)

class GAP_ANALYSIS_NO_JOBS(AppError):
    def __init__(self):
        super().__init__("GAP_ANALYSIS_NO_JOBS", "Not enough job data in your area to run an analysis.", 400)


# Rough weeks to reach intermediate level, per skill category.
# Update these values to adjust roadmap time estimates.
LEARNABILITY_WEEKS = {
  "technical": 8, "tool": 4, "domain": 12,
  "soft": 3, "language": 6
}

# Per-skill overrides (more specific than category-level)
SKILL_LEARNABILITY_OVERRIDES = {
  "python": 10, "excel": 3, "tally": 3, "english": 8,
  "driving": 4, "welding": 6, "ev repair": 12,
  "digital marketing": 6, "ms office": 3
}

def _proficiency_label(n: int) -> str:
    return {
        1: "Beginner", 2: "Elementary", 3: "Intermediate",
        4: "Advanced", 5: "Expert"
    }.get(n, "Unknown")

async def compute_gap(user_id: str) -> dict:
    """
    Compares user's skill profile against job market requirements.
    Returns categorized strengths, gaps, and partial matches.
    No LLM involved — pure DB + scoring math.
    """
    db = get_supabase()

    # Fetch user skills
    profile = db.table("user_skill_profiles").select("*").eq(
        "user_id", user_id
    ).limit(1).execute()

    if not profile.data or not profile.data[0].get("skills"):
        raise GAP_ANALYSIS_NO_SKILLS()

    user_skills = {
        s["skill_name"].lower(): s
        for s in profile.data[0]["skills"] if "skill_name" in s
    }

    # Fetch user preferences and location
    prefs = db.table("user_preferences").select("*").eq(
        "user_id", user_id
    ).limit(1).execute()
    user_prefs = prefs.data[0] if prefs.data else {}
    career_interests = user_prefs.get("career_interests") or []

    user_profile = db.table("user_profiles").select(
        "state"
    ).eq("user_id", user_id).limit(1).execute()
    state = (
        user_profile.data[0].get("state")
        if user_profile.data else None
    )

    # Fetch matching jobs
    jobs_query = (
        db.table("job_listings")
        .select("required_skills, salary_max, category")
        .eq("is_active", True)
    )
    if state:
        jobs_query = jobs_query.eq("location_state", state)
    if career_interests:
        jobs_query = jobs_query.in_("category", career_interests)

    jobs_result = jobs_query.limit(200).execute()
    jobs = jobs_result.data or []

    if not jobs:
        raise GAP_ANALYSIS_NO_JOBS()

    total_jobs = len(jobs)
    logger.info(
        f"[GAP_ANALYSIS] Analyzing {total_jobs} jobs for "
        f"user={user_id}. state={state}"
    )

    # Build required skills frequency map
    required_map = {}
    for job in jobs:
        for skill in (job.get("required_skills") or []):
            key = skill.lower().strip()
            if key not in required_map:
                required_map[key] = {
                    "count": 0, "salary_total": 0, "salary_count": 0
                }
            required_map[key]["count"] += 1
            if job.get("salary_max"):
                required_map[key]["salary_total"] += job["salary_max"]
                required_map[key]["salary_count"] += 1

    # Compute max salary for normalization
    max_salary = max(
        (v["salary_total"] / v["salary_count"]
         for v in required_map.values() if v["salary_count"] > 0),
        default=1
    )

    strengths, gaps, partial_matches = [], [], []

    for skill_name, data in required_map.items():
        frequency_pct = round(data["count"] / total_jobs * 100, 1)
        avg_salary = (
            data["salary_total"] / data["salary_count"]
            if data["salary_count"] > 0 else 0
        )
        salary_uplift = round(avg_salary / max_salary, 3)

        user_entry = user_skills.get(skill_name)
        user_prof = user_entry["proficiency_numeric"] if user_entry else 0
        required_level = 3  # Intermediate is the default job requirement

        skill_category = (
            user_entry.get("category", "technical") if user_entry
            else "technical"
        )
        learnability_weeks = SKILL_LEARNABILITY_OVERRIDES.get(
            skill_name,
            LEARNABILITY_WEEKS.get(skill_category, 8)
        )
        learnability_score = max(0.1, 1.0 - (learnability_weeks / 24))

        if user_prof == 0:
            priority_score = round(
                (frequency_pct / 100) * 0.40 +
                salary_uplift * 0.35 +
                learnability_score * 0.25,
                4
            )
            gaps.append({
                "skill_name": skill_name,
                "category": skill_category,
                "priority_score": priority_score,
                "frequency_pct": frequency_pct,
                "salary_uplift": salary_uplift,
                "learnability_weeks": learnability_weeks,
                "recommended_resources": []
            })
        elif user_prof < required_level:
            partial_matches.append({
                "skill_name": skill_name,
                "current_level": user_prof,
                "current_label": _proficiency_label(user_prof),
                "required_level": required_level,
                "gap_size": required_level - user_prof
            })
        else:
            strengths.append({
                "skill_name": skill_name,
                "proficiency_label": _proficiency_label(user_prof),
                "job_demand_pct": frequency_pct,
                "message": (
                    f"In demand in {frequency_pct}% of jobs in your area"
                )
            })

    gaps.sort(key=lambda x: x["priority_score"], reverse=True)

    logger.info(
        f"[GAP_ANALYSIS] Computed for user={user_id}. "
        f"Strengths={len(strengths)} Gaps={len(gaps)} "
        f"Partial={len(partial_matches)} Jobs={total_jobs}"
    )

    return {
        "strengths": strengths,
        "gaps": gaps,
        "partial_matches": partial_matches,
        "total_jobs_analyzed": total_jobs
    }
