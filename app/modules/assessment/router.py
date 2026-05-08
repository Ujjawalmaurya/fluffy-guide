import asyncio
from typing import List
from fastapi import APIRouter, Depends
from app.modules.assessment.service import AssessmentService
from app.modules.assessment.repository import AssessmentRepository
from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.schemas.request.assessment import AssessmentAnswerRequest
from app.schemas.response.assessment import (
    StartAssessmentResponse, AnswerResponse, 
    AssessmentStatusResponse, AssessmentHistoryItem
)
from app.shared.dependencies import get_current_user, get_db
from app.shared.response_models import APIResponse, ok
from app.core.logger import get_logger

logger = get_logger("ASSESSMENT_ROUTER")
router = APIRouter(prefix="/assessment", tags=["Assessment"])

def get_assessment_service(db=Depends(get_db), llm=Depends(get_ollama_instance)):
    return AssessmentService(AssessmentRepository(db), llm_provider=llm)

async def _get_user_profile(user_id: str, repo: AssessmentRepository) -> dict:
    data = await repo.get_user_profile_and_prefs(user_id)
    return {**data["profile"], **data["preferences"], "user_id": user_id}

@router.post("/start", response_model=APIResponse[StartAssessmentResponse])
async def start_assessment(
    current_user: dict = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    user_profile = await _get_user_profile(current_user["id"], service.repo)
    result = await service.start_assessment(user_id=current_user["id"], user_profile=user_profile)
    return ok(data=result)

@router.post("/answer", response_model=APIResponse[AnswerResponse])
async def submit_answer(
    body: AssessmentAnswerRequest,
    current_user: dict = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    user_profile = await _get_user_profile(current_user["id"], service.repo)
    result = await service.submit_answer(session_id=body.session_id, answer=body.answer, user_id=current_user["id"], user_profile=user_profile)
    return ok(data=result)

@router.get("/status", response_model=APIResponse[AssessmentStatusResponse])
async def get_status(
    current_user: dict = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    user_id = current_user["id"]
    
    # Run eligibility and last completion time in parallel
    results = await asyncio.gather(
        service.check_retake_eligibility(user_id),
        service.repo.get_last_completed_at(user_id)
    )
    
    eligibility = results[0]
    last_completed = results[1]

    # Sync query (Supabase-py is sync by default)
    user_res = service.repo.db.table("users").select("quick_assessment_done").eq("id", user_id).single().execute()
    
    has_completed = user_res.data["quick_assessment_done"] if user_res.data else False
    
    return ok(data={
        **eligibility, 
        "can_retake": eligibility["eligible"], 
        "has_completed": has_completed,
        "last_completed_at": last_completed
    })

@router.get("/history", response_model=APIResponse[List[AssessmentHistoryItem]])
async def get_history(
    current_user: dict = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    sessions = await service.repo.get_history(current_user["id"])
    history = [{
        "session_id": s["id"], "retake_number": s["retake_number"], "is_complete": s["is_complete"],
        "completed_at": s.get("completed_at"), "skills_count": len(s.get("extracted_proficiency") or []),
        "created_at": s["created_at"]
    } for s in sessions]
    return ok(data=history)
