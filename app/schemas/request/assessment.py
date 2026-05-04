"""
Assessment Request Schemas
Handles starting and submitting assessments.
"""
from typing import List, Optional, Any
from pydantic import Field
from app.schemas.base import BaseSchema
from app.schemas.enums import AssessmentType


class AssessmentStartRequest(BaseSchema):
    """Request to start a new assessment session."""
    user_id: Optional[str] = None
    type: AssessmentType = AssessmentType.QUIZ
    domain: Optional[str] = Field(None, description="The subject area, e.g., 'Digital Literacy' or 'Plumbing'")


class AssessmentAnswerRequest(BaseSchema):
    """Request to submit a single assessment answer."""
    session_id: str = Field(..., description="Active session ID")
    answer: str = Field(..., min_length=1, description="User answer to current question")


class AssessmentBulkSubmitRequest(BaseSchema):
    """Request to submit multiple assessment answers at once (optional future use)."""
    session_id: str
    answers: List[dict]
