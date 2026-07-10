# [GAP_ANALYSIS] Cache logic and report orchestration.
# Returns cached report if fresh. Recomputes only when needed.

import asyncio
from datetime import datetime, timezone
from app.modules.gap_analysis import (
    gap_engine, roadmap_builder, repository, profile_hasher
)
from app.core.database import get_async_supabase
from app.core.logger import get_logger

logger = get_logger("GAP_ANALYSIS")

async def get_or_compute_report(
    user_id: str,
    force_recompute: bool = False,
    llm_provider = None
) -> dict:
    """
    Primary entry point for gap analysis.
    Returns cached report if profile hash matches.
    Recomputes (with LLM roadmap call) only when:
        - force_recompute=True (user clicked Re-run)
        - No existing report
        - Report is marked stale
        - Profile hash has changed since last computation
    """
    if llm_provider is None:
        from app.shared.dependencies import get_structured_provider
        llm_provider = get_structured_provider()
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
        return {
            **existing,
            "from_cache": True,
            "motivational_note": existing.get("llm_raw_output", "")
        }

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

    # Fetch combined user profile for roadmap context concurrently using native async calls
    db = await get_async_supabase()

    user_task = db.table("users").select("user_type, preferred_lang").eq("id", user_id).limit(1).execute()
    profile_task = db.table("user_profiles").select("full_name, state").eq("user_id", user_id).limit(1).execute()
    prefs_task = db.table("user_preferences").select("career_interests").eq("user_id", user_id).limit(1).execute()

    user_res, profile_res, prefs_res = await asyncio.gather(
        user_task, profile_task, prefs_task
    )

    user_profile_data = {
        **(user_res.data[0] if user_res.data else {}),
        **(profile_res.data[0] if profile_res.data else {}),
        **(prefs_res.data[0] if prefs_res.data else {})
    }

    # Build roadmap (LLM call) only if we have gaps
    if gap_data["gaps"]:
        roadmap_data, enriched_gaps = await roadmap_builder.build_roadmap(
            user_id, gap_data["gaps"], user_profile_data, llm_provider
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
        "llm_raw_output": roadmap_data.get("motivational_note", "")
    })

    return {**report, "from_cache": False,
            "motivational_note": roadmap_data.get("motivational_note")}
