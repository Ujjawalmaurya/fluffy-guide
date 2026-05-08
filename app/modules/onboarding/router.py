"""
Onboarding router — HTTP layer only.
Calls service for business logic, returns standard responses.
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional

from app.schemas.request.onboarding import (
    UserTypeRequest, ProfileRequest, PreferencesRequest, StudentOnboardingRequest, BlueCollarOnboardingRequest,
    InformalWorkerOnboardingRequest, EmployerOnboardingRequest, NGOOnboardingRequest, GovtOfficerOnboardingRequest, 
    GenerateQuestionsRequest, SubmitAnswersRequest
)
from app.schemas.response.onboarding import (
    OnboardingStateResponse, QuestionsListResponse, SimpleOnboardingResponse, OnboardingSubmitResponse
)
from app.modules.onboarding.service import OnboardingService
from app.modules.onboarding.repository import OnboardingRepository
from app.modules.onboarding.sse_processor import process_stream
from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.shared.dependencies import get_db, get_current_user
from app.shared.response_models import ok, APIResponse

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


def _get_service(db=Depends(get_db), llm=Depends(get_ollama_instance)) -> OnboardingService:
    return OnboardingService(OnboardingRepository(db), llm)


@router.post("/student", response_model=APIResponse)
async def student_onboarding(
    body: StudentOnboardingRequest,
    step: int = Query(1),
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    """Multi-step student onboarding endpoint."""
    result = await service.save_student_onboarding(current_user["id"], body, step)
    return ok(data=result, message=f"Step {step} saved successfully.")


@router.post("/blue-collar", response_model=APIResponse)
@router.post("/blue_collar", response_model=APIResponse)
async def blue_collar_onboarding(
    body: BlueCollarOnboardingRequest,
    step: int = Query(1),
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    """Multi-step blue collar worker onboarding endpoint."""
    result = await service.save_blue_collar_onboarding(current_user["id"], body, step)
    return ok(data=result, message=f"Step {step} saved successfully.")


@router.post("/user-type", response_model=APIResponse)
async def set_user_type(
    body: UserTypeRequest,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    await service.set_user_type(current_user["id"], body)
    return ok(message="User type saved.")


@router.post("/profile", response_model=APIResponse)
async def save_profile(
    body: ProfileRequest,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    await service.save_profile(current_user["id"], body)
    return ok(message="Profile saved.")


@router.post("/preferences", response_model=APIResponse)
async def save_preferences(
    body: PreferencesRequest,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    await service.save_preferences(current_user["id"], body)
    return ok(message="Preferences saved.")


@router.post("/generate-questions", response_model=APIResponse[QuestionsListResponse])
async def generate_questions(
    body: GenerateQuestionsRequest,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    questions = await service.generate_questions(current_user["id"], body)
    return ok(data={"questions": questions})


@router.post("/informal-worker", response_model=APIResponse[SimpleOnboardingResponse])
@router.post("/informal_worker", response_model=APIResponse[SimpleOnboardingResponse])
async def onboarding_informal_worker(
    data: InformalWorkerOnboardingRequest,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service)
):
    result = await service.save_informal_worker_onboarding(current_user["id"], data)
    return ok(data=result)


@router.post("/employer", response_model=APIResponse[SimpleOnboardingResponse])
async def onboarding_employer(
    data: EmployerOnboardingRequest,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service)
):
    result = await service.save_employer_onboarding(current_user["id"], data)
    return ok(data=result)


@router.post("/ngo", response_model=APIResponse[SimpleOnboardingResponse])
async def onboarding_ngo(
    data: NGOOnboardingRequest,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service)
):
    result = await service.save_ngo_onboarding(current_user["id"], data)
    return ok(data=result)


@router.post("/govt", response_model=APIResponse[SimpleOnboardingResponse])
@router.post("/government", response_model=APIResponse[SimpleOnboardingResponse])
async def onboarding_govt(
    data: GovtOfficerOnboardingRequest,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service)
):
    result = await service.save_govt_onboarding(current_user["id"], data)
    return ok(data=result)


@router.post("/submit-answers", response_model=APIResponse[OnboardingSubmitResponse])
async def submit_answers(
    body: SubmitAnswersRequest,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    session_id = await service.submit_answers(current_user["id"], body)
    return ok(data={"session_id": session_id})


@router.get("/process-stream")
async def process_stream_endpoint(
    session_id: str,
    token: str = None,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    repo = OnboardingRepository(db)
    return StreamingResponse(
        process_stream(session_id, repo),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/state", response_model=APIResponse[OnboardingStateResponse])
async def get_state(
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    state = await service.get_state(current_user["id"])
    return ok(data=state)
