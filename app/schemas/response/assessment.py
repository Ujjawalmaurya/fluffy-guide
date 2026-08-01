"""
Assessment Response Schemas
Results and feedback for assessments.
"""
from typing import List, Optional, Any
from datetime import datetime
from pydantic import Field
from app.schemas.base import BaseSchema
from app.schemas.enums import SkillLevel


class ImprovementArea(BaseSchema):
    """Specific topic or skill to improve."""
    topic: str
    feedback: str
    suggested_resources: List[str] = []


class AssessmentResultResponse(BaseSchema):
    """Final result of an assessment."""
    score: float = Field(..., ge=0, le=100)
    skill_level: SkillLevel
    strengths: List[str]
    improvement_areas: List[ImprovementArea]
    summary: str


class QuestionResponse(BaseSchema):
    """Response containing a single question within a batch."""
    question: str
    question_type: str = "mcq"
    options: List[str] = Field(default_factory=list)
    allows_multiple: bool = False
    allows_other: bool = True
    skill_probing: str = "general"


class AssessmentBatchResponse(BaseSchema):
    """A batch of questions returned by the adaptive engine."""
    questions: List[QuestionResponse]
    phase: int
    phase_name: str


class StartAssessmentResponse(BaseSchema):
    """Response after starting/resuming an assessment."""
    session_id: str
    batch: AssessmentBatchResponse
    phase: int
    phase_name: str
    question_number: int
    retakes_used: int
    retakes_remaining: int
    max_retakes: int
    can_resume: bool
    is_complete: bool = False
    eligible: bool = True
    has_incomplete: bool = False
    incomplete_session_id: Optional[str] = None


class AnswerResponse(BaseSchema):
    """Feedback after submitting an answer."""
    session_id: str
    batch: Optional[AssessmentBatchResponse] = None
    phase: Optional[int] = None
    question_number: Optional[int] = None
    is_complete: bool
    retakes_remaining: int
    # Populated only when is_complete=True
    skills_found: Optional[List[Any]] = None
    career_goals: Optional[List[str]] = None
    assessment_summary: Optional[str] = None


class AssessmentStatusResponse(BaseSchema):
    """Current assessment status and eligibility for user."""
    has_completed: bool
    retakes_used: int
    retakes_remaining: int
    max_retakes: int
    last_completed_at: Optional[datetime] = None
    can_retake: bool
    eligible: bool # Added for consistency with service response
    next_retake_available_at: Optional[datetime] = None
    has_incomplete: bool
    incomplete_session_id: Optional[str] = None


class AssessmentHistoryItem(BaseSchema):
    """Summary of a past assessment session."""
    session_id: str
    retake_number: int
    is_complete: bool
    completed_at: Optional[datetime] = None
    skills_count: int
    created_at: datetime


class LatestAssessmentResponse(BaseSchema):
    """Summary of the user's latest completed assessment session."""
    session_id: str
    is_complete: bool
    skills_found: List[Any] = Field(default_factory=list)
    assessment_summary: str
    completed_at: Optional[datetime] = None
    retakes_remaining: int
    can_retake: bool

