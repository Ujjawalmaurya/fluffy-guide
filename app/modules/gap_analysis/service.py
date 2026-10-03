# [GAP_ANALYSIS] Cache logic and report orchestration.
# Returns cached report if fresh. Recomputes only when needed.

from datetime import datetime, timezone
from app.modules.gap_analysis import (
    gap_engine, roadmap_builder, repository, profile_hasher
)
from app.core.database import get_supabase
from app.core.logger import get_logger

logger = get_logger("GAP_ANALYSIS")

async def get_or_compute_report(
    user_id: str,
    force_recompute: bool = False,
    gemini_provider = None
) -> dict:
    """
    Primary entry point for gap analysis.
    Returns cached report if profile hash matches.
    Recomputes (with Gemini roadmap call) only when:
        - force_recompute=True (user clicked Re-run)
        - No existing report
        - Report is marked stale
        - Profile hash has changed since last computation
    """
    current_hash = await profile_hasher.compute_hash(user_id)
    existing = await repository.get_by_user_id(user_id)

    needs_compute = (
        force_recompute
        or existing is None
        or existing.get("is_stale")
        or existing.get("profile_hash") != current_hash
    )

    if not needs_compute:
        logger.info(
            f"[GAP_ANALYSIS] Cache hit for user={user_id}. "
            f"Computed {existing.get('computed_at')}"
        )
        return {**existing, "from_cache": True}

    reason = (
        "forced" if force_recompute
        else ("new" if not existing else "stale")
    )
    logger.info(
        f"[GAP_ANALYSIS] Recomputing for user={user_id}. "
        f"reason={reason}"
    )

    # Compute gap (no LLM)
    gap_data = await gap_engine.compute_gap(user_id)

    # Fetch combined user profile for roadmap context
    db = get_supabase()
    user_row = db.table("users").select(
        "user_type, preferred_lang"
    ).eq("id", user_id).limit(1).execute()
    profile_row = db.table("user_profiles").select(
        "full_name, state"
    ).eq("user_id", user_id).limit(1).execute()
    prefs_row = db.table("user_preferences").select(
        "career_interests"
    ).eq("user_id", user_id).limit(1).execute()

    user_profile_data = {
        **(user_row.data[0] if user_row.data else {}),
        **(profile_row.data[0] if profile_row.data else {}),
        **(prefs_row.data[0] if prefs_row.data else {})
    }

    # Build roadmap (Gemini call) only if we have gaps
    if gap_data["gaps"]:
        roadmap_data, enriched_gaps = await roadmap_builder.build_roadmap(
            user_id, gap_data["gaps"], user_profile_data, gemini_provider
        )
    else:
        roadmap_data = {"roadmap": [], "motivational_note": "Keep building your skills!"}
        enriched_gaps = []

    gap_data["gaps"] = enriched_gaps

    now = datetime.now(timezone.utc).isoformat()
    report = await repository.upsert(user_id, {
        "strengths": gap_data["strengths"],
        "gaps": enriched_gaps,
        "partial_matches": gap_data["partial_matches"],
        "roadmap": roadmap_data.get("roadmap", []),
        "total_jobs_analyzed": gap_data["total_jobs_analyzed"],
        "profile_hash": current_hash,
        "is_stale": False,
        "computed_at": now,
        "gemini_raw_output": str(roadmap_data)[:2000]
    })

    return {**report, "from_cache": False,
            "motivational_note": roadmap_data.get("motivational_note")}
