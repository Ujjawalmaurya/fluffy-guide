"""
router.py — FastAPI endpoints for resume analysis and bullet improvements.
Prefix: /resume (mounted with /api/v1 prefix in main.py)
"""
import time
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from loguru import logger

from app.shared.dependencies import get_current_user, get_db
from app.core.config import settings
from app.modules.resume_analysis.schemas import (
    ResumeAnalysisResult,
    BulletImprovement,
    ImproveBulletRequest,
)
from app.modules.resume_analysis.service import ResumeAnalysisService
from app.modules.resume_analysis.repository import ResumeAnalysisRepository
from app.modules.resume_analysis.suggester import improve_bullet
from app.modules.resume_analysis.rate_limiter import (
    check_bullet_rate_limit,
    increment_bullet_rate_limit,
)

router = APIRouter(prefix="/resume", tags=["resume-analysis"])


@router.post("/analyze", response_model=ResumeAnalysisResult)
async def analyze_resume(
    file: UploadFile = File(...),
    target_roles: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Analyzes a PDF resume and returns a detailed structured report.
    Uses multi-stage deterministic pre-flight + AI extraction pipeline.
    """
    start_time = time.time()

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    content = await file.read()
    if len(content) > settings.resume_analysis_max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {settings.resume_analysis_max_file_size_mb}MB allowed.",
        )

    roles_list = [r.strip() for r in target_roles.split(",") if r.strip()] if target_roles else []

    try:
        repo = ResumeAnalysisRepository(db)
        service = ResumeAnalysisService(repo)
        result = await service.analyze(
            user_id=current_user["id"],
            file_content=content,
            target_roles=roles_list,
        )

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"[RESUME_ROUTER] total_time={duration_ms}ms user_id={current_user['id']}")
        return result
    except Exception as e:
        logger.error(f"[RESUME_ROUTER] Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while analyzing your resume.")


@router.get("/analysis", response_model=Optional[ResumeAnalysisResult])
async def get_latest_analysis(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Returns the latest resume analysis for the current user."""
    repo = ResumeAnalysisRepository(db)
    return repo.get_latest_analysis(current_user["id"])


@router.get("/score-breakdown")
async def get_score_breakdown(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Returns scores and flags for dashboard widgets."""
    repo = ResumeAnalysisRepository(db)
    return repo.get_score_breakdown(current_user["id"])


@router.post("/improve-bullet", response_model=BulletImprovement)
async def improve_single_bullet(
    request: ImproveBulletRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Improves a single bullet point using active LLM. Daily rate limited."""
    allowed = await check_bullet_rate_limit(current_user["id"], db)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit of {settings.resume_bullet_daily_limit} improvements reached. Try again tomorrow.",
        )

    role_context = request.target_roles[0] if request.target_roles else None
    improvement = await improve_bullet(request.bullet, role_context)
    await increment_bullet_rate_limit(current_user["id"], db)
    return improvement
