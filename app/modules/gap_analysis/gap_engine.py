# [GAP_ANALYSIS] Core gap computation — no LLM calls here.
# Pure data: compares user skills against job market requirements.

import asyncio
from app.core.database import get_async_supabase
from app.core.logger import get_logger
from app.shared.exceptions import AppError
import difflib

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

import re

# Semantic aliases to help match skills that are named differently
# Format: { "required_skill_name": ["alias1", "alias2", ...] }
SKILL_ALIASES = {
    "apis": ["rest apis", "backend", "fastapi", "flask", "api development", "ai/backend", "node.js"],
    "backend": ["ai/backend", "node.js", "django", "golang", "server side", "python", "fastapi", "rest apis", "microservices"],
    "frontend": ["react", "angular", "vue", "javascript", "css", "html", "web dev", "next.js", "typescript", "frontend developer"],
    "automation": ["zapier", "make.com", "python", "automation specialist", "scripting", "no-code"],
    "ms office": ["excel", "word", "powerpoint", "tally", "spreadsheet", "data entry"],
    "digital marketing": ["social media", "seo", "content writing", "ads", "marketing", "branding"],
    "soft skills": ["problem solving", "communication", "teamwork", "leadership", "critical thinking", "adaptability"]
}

def _find_matching_skill(skill_name: str, user_skills: dict) -> dict | None:
    """
    Finds a user skill that matches the required skill_name using:
    1. Exact match (lowercased)
    2. Substring match (word boundaries)
    3. Semantic alias match (checking both directions)
    4. Fuzzy match (difflib)
    """
    skill_name = skill_name.lower().strip()
    
    # 1. Exact match
    if skill_name in user_skills:
        return user_skills[skill_name]
    
    # 2. Substring match with word boundaries
    # Using regex to ensure we match "c" in "c language" but not in "javascript"
    for u_skill in user_skills:
        pattern = rf"\b{re.escape(skill_name)}\b"
        if re.search(pattern, u_skill):
            return user_skills[u_skill]
        
        pattern_rev = rf"\b{re.escape(u_skill)}\b"
        if re.search(pattern_rev, skill_name):
            return user_skills[u_skill]
            
    # 3. Semantic Alias match
    # Check if the required skill or any user skill belongs to the same alias group
    for req_key, aliases in SKILL_ALIASES.items():
        group = [req_key] + aliases
        # If the required skill is in this group
        if skill_name in group:
            # Check if the user has ANY skill from this group
            for member in group:
                if member in user_skills:
                    return user_skills[member]
        
    # 4. Fuzzy match
    close_matches = difflib.get_close_matches(skill_name, list(user_skills.keys()), n=1, cutoff=0.7)
    if close_matches:
        return user_skills[close_matches[0]]
        
    return None

def _proficiency_label(n: int) -> str:
    return {
        1: "Beginner", 2: "Elementary", 3: "Intermediate",
        4: "Advanced", 5: "Expert"
    }.get(n, "Unknown")

CATEGORY_MAPPING = {
    "software": "technology",
    "it": "technology",
    "coding": "technology",
    "teaching": "education",
    "school": "education",
    "farming": "agriculture",
    "construction": "construction",
    "building": "construction",
    "sales": "retail",
    "marketing": "retail",
    "bank": "finance",
    "accounting": "finance",
    "hotel": "hospitality",
    "tourism": "hospitality",
    "factory": "manufacturing",
    "doctor": "healthcare",
    "nurse": "healthcare",
    "delivery": "logistics",
    "driving": "logistics"
}

def _map_interests(interests: list) -> list[str]:
    mapped = set()
    for i in interests:
        # Robust string conversion and extraction
        if isinstance(i, dict):
            val = str(i.get("label") or i.get("value") or i)
        else:
            val = str(i)
            
        low_i = val.lower()
        mapped.add(low_i)  # Add original
        for key, val_mapped in CATEGORY_MAPPING.items():
            if key in low_i:
                mapped.add(val_mapped)
    return list(mapped)

async def compute_gap(user_id: str) -> dict:
    """
    Compares user's skill profile against job market requirements.
    Returns categorized strengths, gaps, and partial matches.
    No LLM involved — pure DB + scoring math.
    """
    db = await get_async_supabase()

    # Execute all 3 initial queries concurrently using native async calls
    profile_task = db.table("user_skill_profiles").select("*").eq("user_id", user_id).limit(1).execute()
    prefs_task = db.table("user_preferences").select("*").eq("user_id", user_id).limit(1).execute()
    user_profile_task = db.table("user_profiles").select("state").eq("user_id", user_id).limit(1).execute()

    profile_result, prefs_result, user_profile_result = await asyncio.gather(
        profile_task, prefs_task, user_profile_task
    )

    if not profile_result.data or not profile_result.data[0].get("skills"):
        raise GAP_ANALYSIS_NO_SKILLS()

    user_skills = {
        s["skill_name"].lower(): s
        for s in profile_result.data[0]["skills"] if "skill_name" in s
    }

    user_prefs = prefs_result.data[0] if prefs_result.data else {}
    career_interests = user_prefs.get("career_interests") or []

    state = (
        user_profile_result.data[0].get("state")
        if user_profile_result.data else None
    )

    # Normalize state casing from snake_case (e.g. uttar_pradesh) to Title Case (e.g. Uttar Pradesh)
    normalized_state = state.replace("_", " ").title() if state else None

    # Fetch matching jobs with fallback
    mapped_interests = _map_interests(career_interests)
    logger.info(f"[GAP_ENGINE] mapped_interests={mapped_interests}, state={normalized_state}")
    
    # Try 1: Exact match (State + Interests)
    jobs_query = db.table("job_listings").select("required_skills, salary_max, category").eq("is_active", True)
    if normalized_state:
        jobs_query = jobs_query.eq("location_state", normalized_state)
    if mapped_interests:
        jobs_query = jobs_query.in_("category", mapped_interests)
    
    jobs_result = await jobs_query.limit(200).execute()
    jobs = jobs_result.data or []
    logger.info(f"[GAP_ENGINE] Try 1 (Exact): Found {len(jobs)} jobs")
    match_type = "local_targeted"

    # Try 2: Interests only (National)
    if not jobs and mapped_interests:
        jobs_result = await db.table("job_listings").select("required_skills, salary_max, category").eq("is_active", True).in_("category", mapped_interests).limit(200).execute()
        jobs = jobs_result.data or []
        logger.info(f"[GAP_ENGINE] Try 2 (Interests Only): Found {len(jobs)} jobs")
        match_type = "national_targeted"

    # Try 3: State only (All categories)
    if not jobs and normalized_state:
        jobs_result = await db.table("job_listings").select("required_skills, salary_max, category").eq("is_active", True).eq("location_state", normalized_state).limit(200).execute()
        jobs = jobs_result.data or []
        logger.info(f"[GAP_ENGINE] Try 3 (State Only): Found {len(jobs)} jobs")
        match_type = "local_broad"

    # Try 4: All active jobs (Global baseline)
    if not jobs:
        jobs_result = await db.table("job_listings").select("required_skills, salary_max, category").eq("is_active", True).limit(200).execute()
        jobs = jobs_result.data or []
        logger.info(f"[GAP_ENGINE] Try 4 (Global): Found {len(jobs)} jobs")
        match_type = "all_active"

    total_jobs = len(jobs)
    if total_jobs == 0:
        logger.warning(f"[GAP_ANALYSIS] No job data found at all. Analysis will only show strengths.")
    else:
        logger.info(
            f"[GAP_ANALYSIS] Analyzing {total_jobs} jobs for "
            f"user={user_id}. match_type={match_type}, state={normalized_state}"
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
        frequency_pct = round(data["count"] / total_jobs * 100, 1) if total_jobs > 0 else 0
        avg_salary = (
            data["salary_total"] / data["salary_count"]
            if data["salary_count"] > 0 else 0
        )
        salary_uplift = round(avg_salary / max_salary, 3)

        user_entry = _find_matching_skill(skill_name, user_skills)
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
