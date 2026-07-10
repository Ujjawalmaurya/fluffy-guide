# [GAP_ANALYSIS] Computes a SHA256 hash of the user's current
# profile state. When hash changes, cached report is marked stale.

import asyncio
import hashlib
from app.core.database import get_async_supabase
from app.core.logger import get_logger

logger = get_logger("GAP_ANALYSIS")

async def compute_hash(user_id: str) -> str:
    """
    Produces a deterministic hash of the user's skill profile state.
    Hash inputs: sorted skill names + resume timestamp +
                 last assessment timestamp + preferences timestamp.
    Any change in these = different hash = stale report.
    """
    db = await get_async_supabase()

    # Execute all 4 queries concurrently using native async calls
    skills_task = db.table("user_skill_profiles").select("skills").eq("user_id", user_id).limit(1).execute()
    resume_task = db.table("profile_enrichments").select("resume_uploaded_at").eq("user_id", user_id).limit(1).execute()
    session_task = (
        db.table("questionnaire_sessions")
        .select("completed_at")
        .eq("user_id", user_id)
        .eq("assessment_type", "quick_assessment")
        .eq("is_complete", True)
        .order("completed_at", desc=True)
        .limit(1)
        .execute()
    )
    prefs_task = db.table("user_preferences").select("updated_at").eq("user_id", user_id).limit(1).execute()

    skills_result, resume_result, session_result, prefs_result = await asyncio.gather(
        skills_task, resume_task, session_task, prefs_task
    )

    skills = skills_result.data[0]["skills"] if skills_result.data and skills_result.data[0].get("skills") else []
    skill_names = sorted([
        s["skill_name"].lower() for s in skills if "skill_name" in s
    ])

    resume_at = str(
        resume_result.data[0].get("resume_uploaded_at", "")
        if resume_result.data else ""
    )

    assessment_at = str(
        session_result.data[0].get("completed_at", "")
        if session_result.data else ""
    )

    prefs_at = str(
        prefs_result.data[0].get("updated_at", "")
        if prefs_result.data else ""
    )

    raw = "|".join(skill_names) + resume_at + assessment_at + prefs_at
    hash_val = hashlib.sha256(raw.encode()).hexdigest()

    logger.debug(
        f"[GAP_ANALYSIS] Hash for user={user_id}: {hash_val[:8]}..."
    )
    return hash_val
