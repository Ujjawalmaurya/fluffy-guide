# [ASSESSMENT] HTTP endpoints for assessment module.
# Thin layer — parses request, calls service, returns response.
# All business logic lives in service.py.

from fastapi import APIRouter, Depends
from app.modules.assessment import service
from app.modules.assessment.schemas import (
    SubmitAnswerRequest, StartAssessmentResponse,
    AnswerResponse, AssessmentStatusResponse
)
from app.shared.dependencies import get_current_user
from app.shared.response_models import APIResponse
from app.core.logger import get_logger

logger = get_logger("ASSESSMENT_ROUTER")
router = APIRouter(prefix="/assessment", tags=["Assessment"])

# Helper to build combined user+profile dict for service calls
async def _get_user_profile(current_user: dict) -> dict:
    """
    Fetches and merges user + user_profiles + user_preferences
    into a single dict for passing to service/engine functions.
    """
    from app.core.database import get_supabase
    db = get_supabase()
    user_id = current_user["id"]
    
    profile = db.table("user_profiles").select("*").eq(
        "user_id", user_id
    ).limit(1).execute()
    
    prefs = db.table("user_preferences").select("*").eq(
        "user_id", user_id
    ).limit(1).execute()
    
    profile_data = profile.data[0] if profile.data else {}
    prefs_data = prefs.data[0] if prefs.data else {}
    
    return {
        **current_user,
        **profile_data,
        **prefs_data,
        "user_id": user_id
    }

@router.post("/start", response_model=APIResponse)
async def start_assessment(
    current_user: dict = Depends(get_current_user)
):
    """
    Starts a new assessment or resumes an existing incomplete session.
    Returns the first (or current) question with session metadata.
    """
    from app.modules.ai_chat.providers.openai_provider import get_openai_instance
    from app.modules.ai_chat.providers.gemini import get_gemini_instance
    
    user_profile = await _get_user_profile(current_user)
    
    result = await service.start_assessment(
        user_id=current_user["id"],
        user_profile=user_profile,
        openai_provider=get_openai_instance(),
        gemini_provider=get_gemini_instance()
    )
    
    logger.info(
        f"[ASSESSMENT] /start called. user={current_user['id']}. "
        f"can_resume={result.get('can_resume')}"
    )
    
    return APIResponse(success=True, data=result)

@router.post("/answer", response_model=APIResponse)
async def submit_answer(
    body: SubmitAnswerRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submits an answer to the current question.
    Returns next question OR completion result.
    """
    from app.modules.ai_chat.providers.openai_provider import get_openai_instance
    from app.modules.ai_chat.providers.gemini import get_gemini_instance
    
    user_profile = await _get_user_profile(current_user)
    
    result = await service.submit_answer(
        session_id=body.session_id,
        answer=body.answer,
        user_id=current_user["id"],
        user_profile=user_profile,
        openai_provider=get_openai_instance(),
        gemini_provider=get_gemini_instance()
    )
    
    return APIResponse(success=True, data=result)

@router.get("/status", response_model=APIResponse)
async def get_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns current assessment status for this user.
    Used by frontend to decide what banner/state to show.
    """
    from app.core.database import get_supabase
    
    eligibility = await service.check_retake_eligibility(
        current_user["id"]
    )
    
    user = get_supabase().table("users").select(
        "quick_assessment_done"
    ).eq("id", current_user["id"]).limit(1).execute()
    
    has_completed = (
        user.data[0]["quick_assessment_done"]
        if user.data else False
    )
    
    return APIResponse(success=True, data={
        **eligibility,
        "has_completed": has_completed
    })

@router.get("/history", response_model=APIResponse)
async def get_history(
    current_user: dict = Depends(get_current_user)
):
    """Returns all assessment sessions for current user, newest first."""
    from app.modules.assessment import repository
    sessions = await repository.get_history(current_user["id"])
    
    history = [{
        "session_id": s["id"],
        "retake_number": s["retake_number"],
        "is_complete": s["is_complete"],
        "completed_at": s.get("completed_at"),
        "skills_count": len(s.get("extracted_proficiency") or []),
        "created_at": s["created_at"]
    } for s in sessions]
    
    return APIResponse(success=True, data=history)
