import io
import time
from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from loguru import logger

from app.shared.dependencies import get_current_user, get_db
from app.core.config import settings
from models.resume_analysis_models import ResumeAnalysisResult, BulletImprovement, ImproveBulletRequest
from services.resume_analysis_orchestrator import analyze_resume_pipeline
from services.resume_suggester import improve_bullet_via_groq

router = APIRouter(prefix="/resume", tags=["resume-analysis"])

async def check_rate_limit(user_id: str, db):
    """
    Checks and updates the daily rate limit for bullet improvements.
    """
    now = datetime.now()
    today = date.today()
    
    # Get or create rate limit record
    result = db.table("user_rate_limits").select("*").eq("user_id", user_id).execute()
    
    if not result.data:
        # Create new record
        db.table("user_rate_limits").insert({
            "user_id": user_id,
            "bullet_improvement_count": 0,
            "last_reset_at": now.isoformat()
        }).execute()
        return True
    
    record = result.data[0]
    last_reset = datetime.fromisoformat(record["last_reset_at"].replace('Z', '+00:00')).date()
    
    count = record["bullet_improvement_count"]
    
    if last_reset < today:
        # New day, reset counter
        db.table("user_rate_limits").update({
            "bullet_improvement_count": 0,
            "last_reset_at": now.isoformat()
        }).eq("user_id", user_id).execute()
        return True
    
    if count >= settings.resume_bullet_daily_limit:
        return False
        
    return True

async def increment_rate_limit(user_id: str, db):
    # Get current count
    res = db.table("user_rate_limits").select("bullet_improvement_count").eq("user_id", user_id).single().execute()
    current_count = res.data["bullet_improvement_count"] if res.data else 0
    
    db.table("user_rate_limits").update({
        "bullet_improvement_count": current_count + 1,
        "updated_at": "now()"
    }).eq("user_id", user_id).execute()

@router.post("/analyze", response_model=ResumeAnalysisResult)
async def analyze_resume(
    file: UploadFile = File(...),
    target_roles: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyzes a PDF resume and returns a detailed structured report.
    Uses the production-grade multi-stage extraction pipeline.
    """
    start_time = time.time()
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")
        
    content = await file.read()
    if len(content) > settings.resume_analysis_max_file_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large. Max {settings.resume_analysis_max_file_size_mb}MB allowed.")

    # Parse target_roles from comma-separated string if present
    roles_list = []
    if target_roles:
        roles_list = [r.strip() for r in target_roles.split(",") if r.strip()]

    # Call the orchestrator which handles extraction, AI analysis, scoring, and suggestions
    try:
        result = await analyze_resume_pipeline(
            user_id=current_user["id"],
            file_content=content,
            target_roles=roles_list
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"[RESUME_ANALYSIS_ROUTER] total_time={duration_ms}ms user_id={current_user['id']}")
        
        return result
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS_ROUTER] Unexpected error during analysis: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while analyzing your resume.")

@router.get("/analysis", response_model=Optional[ResumeAnalysisResult])
async def get_latest_analysis(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """
    Returns the latest resume analysis for the current user.
    Returns None if no analysis exists.
    """
    result = db.table("resume_analysis").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(1).execute()
    
    if not result.data:
        return None
        
    return result.data[0]

@router.get("/score-breakdown")
async def get_score_breakdown(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """
    Returns only the scores and flags for dashboard widgets.
    Returns None if no analysis exists yet.
    """
    result = db.table("resume_analysis").select("quality_scores, overall_score, india_flags").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(1).execute()
    
    if not result.data:
        return None
        
    return result.data[0]

@router.post("/improve-bullet", response_model=BulletImprovement)
async def improve_single_bullet(
    request: ImproveBulletRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Improves a single bullet point using Groq. Rate limited.
    """
    allowed = await check_rate_limit(current_user["id"], db)
    if not allowed:
        raise HTTPException(
            status_code=429, 
            detail=f"Daily limit of {settings.resume_bullet_daily_limit} improvements reached. Try again tomorrow."
        )
        
    improvement = await improve_bullet_via_groq(request.bullet, request.target_roles)
    
    # Increment counter
    await increment_rate_limit(current_user["id"], db)
    
    return improvement
