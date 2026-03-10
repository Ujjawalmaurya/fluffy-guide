"""
Onboarding router — HTTP layer only.
Calls service for business logic, returns standard responses.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.modules.onboarding.schemas import (
    UserTypeIn, ProfileIn, PreferencesIn, GenerateQuestionsIn, SubmitAnswersIn
)
from app.modules.onboarding.service import OnboardingService
from app.modules.onboarding.repository import OnboardingRepository
from app.modules.onboarding.sse_processor import process_stream
from app.shared.dependencies import get_db, get_current_user
from app.shared.response_models import ok

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


def _get_service(db=Depends(get_db)) -> OnboardingService:
    return OnboardingService(OnboardingRepository(db))


@router.post("/user-type")
async def set_user_type(
    body: UserTypeIn,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    service.set_user_type(current_user["id"], body)
    return ok(message="User type saved.")


@router.post("/profile")
async def save_profile(
    body: ProfileIn,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    service.save_profile(current_user["id"], body)
    return ok(message="Profile saved.")


@router.post("/preferences")
async def save_preferences(
    body: PreferencesIn,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    service.save_preferences(current_user["id"], body)
    return ok(message="Preferences saved.")


@router.post("/generate-questions")
async def generate_questions(
    body: GenerateQuestionsIn,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    questions = await service.generate_questions(current_user["id"], body)
    return ok(data={"questions": questions})


@router.post("/submit-answers")
async def submit_answers(
    body: SubmitAnswersIn,
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    session_id = service.submit_answers(current_user["id"], body)
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


@router.get("/state")
async def get_state(
    current_user: dict = Depends(get_current_user),
    service: OnboardingService = Depends(_get_service),
):
    state = service.get_state(current_user["id"])
    return ok(data=state)
