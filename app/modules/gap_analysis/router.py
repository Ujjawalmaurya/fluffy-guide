# [GAP_ANALYSIS] HTTP endpoints for gap analysis.

from fastapi import APIRouter, Depends
from app.modules.gap_analysis import service
from app.schemas.response.gap_analysis import GapAnalysisReportResponse
from app.shared.dependencies import get_current_user
from app.shared.response_models import APIResponse, ok
from app.core.config import settings as get_settings
from app.core.logger import get_logger

logger = get_logger("GAP_ANALYSIS_ROUTER")
router = APIRouter(prefix="/gap-analysis", tags=["Gap Analysis"])

@router.get("/report", response_model=APIResponse[GapAnalysisReportResponse])
async def get_report(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns cached gap analysis report.
    Recomputes automatically if stale or missing.
    """
    from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
    ollama = get_ollama_instance()

    report = await service.get_or_compute_report(
        user_id=current_user["id"],
        force_recompute=False,
        llm_provider=ollama
    )
    logger.info(
        f"[GAP_ANALYSIS] /report served. user={current_user['id']}. "
        f"from_cache={report.get('from_cache')}"
    )
    return ok(data=report)

@router.post("/run", response_model=APIResponse[GapAnalysisReportResponse])
async def force_run(
    current_user: dict = Depends(get_current_user)
):
    """
    Forces a fresh recompute regardless of cache state.
    Called when user clicks 'Re-run Analysis'.
    """
    from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
    ollama = get_ollama_instance()

    logger.info(
        f"[GAP_ANALYSIS] Manual recompute. user={current_user['id']}"
    )
    report = await service.get_or_compute_report(
        user_id=current_user["id"],
        force_recompute=True,
        llm_provider=ollama
    )
    return ok(data=report)

@router.get("/roadmap", response_model=APIResponse)
async def get_roadmap(
    current_user: dict = Depends(get_current_user)
):
    """Returns only the roadmap portion of the current report."""
    from app.modules.gap_analysis import repository
    report = await repository.get_by_user_id(current_user["id"])
    if not report:
        return ok(data={"roadmap": [], "message": "Run gap analysis first."})
    
    return ok(data={
        "roadmap": report.get("roadmap", []),
        "motivational_note": report.get("llm_raw_output", "")
    })
