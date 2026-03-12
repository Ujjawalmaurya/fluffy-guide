# [GAP_ANALYSIS] HTTP endpoints for gap analysis.

from fastapi import APIRouter, Depends
from app.modules.gap_analysis import service
from app.shared.dependencies import get_current_user
from app.shared.response_models import APIResponse
from app.core.config import settings as get_settings
from app.core.logger import get_logger

logger = get_logger("GAP_ANALYSIS_ROUTER")
router = APIRouter(prefix="/gap-analysis", tags=["Gap Analysis"])

@router.get("/report", response_model=APIResponse)
async def get_report(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns cached gap analysis report.
    Recomputes automatically if stale or missing.
    """
    from app.modules.ai_chat.providers.gemini import get_gemini_instance
    settings = get_settings
    gemini = get_gemini_instance()

    report = await service.get_or_compute_report(
        user_id=current_user["id"],
        force_recompute=False,
        gemini_provider=gemini
    )
    logger.info(
        f"[GAP_ANALYSIS] /report served. user={current_user['id']}. "
        f"from_cache={report.get('from_cache')}"
    )
    return APIResponse(success=True, data=report)

@router.post("/run", response_model=APIResponse)
async def force_run(
    current_user: dict = Depends(get_current_user)
):
    """
    Forces a fresh recompute regardless of cache state.
    Called when user clicks 'Re-run Analysis'.
    """
    from app.modules.ai_chat.providers.gemini import get_gemini_instance
    settings = get_settings
    gemini = get_gemini_instance()

    logger.info(
        f"[GAP_ANALYSIS] Manual recompute. user={current_user['id']}"
    )
    report = await service.get_or_compute_report(
        user_id=current_user["id"],
        force_recompute=True,
        gemini_provider=gemini
    )
    return APIResponse(success=True, data=report)

@router.get("/roadmap", response_model=APIResponse)
async def get_roadmap(
    current_user: dict = Depends(get_current_user)
):
    """Returns only the roadmap portion of the current report."""
    from app.modules.gap_analysis import repository
    report = await repository.get_by_user_id(current_user["id"])
    if not report:
        return APIResponse(success=True, data={"roadmap": [],
            "message": "Run gap analysis first."})
    return APIResponse(success=True, data={
        "roadmap": report.get("roadmap", []),
        "motivational_note": report.get("gemini_raw_output", "")
    })
