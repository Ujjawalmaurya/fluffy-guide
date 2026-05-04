from typing import List, Dict, Any, Optional
from app.schemas.base import BaseSchema

class OnboardingStateResponse(BaseSchema):
    current_step: int
    completed_steps: List[int]
    step_data: Dict[str, Any]

class QuestionResponse(BaseSchema):
    id: str
    text: str
    type: str # text, choice, multi-choice
    options: List[str] = []
    category: str

class QuestionsListResponse(BaseSchema):
    questions: List[QuestionResponse]

class SimpleOnboardingResponse(BaseSchema):
    percentage: int
    status: str
    redirect: Optional[str] = None

class OnboardingSubmitResponse(BaseSchema):
    session_id: str
    message: str = "Onboarding answers submitted successfully"
