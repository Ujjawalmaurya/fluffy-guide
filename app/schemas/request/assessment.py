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
    """Request to submit assessment answers. Can be a single string or a list (for batches)."""
    session_id: str = Field(..., description="Active session ID")
    answer: Any = Field(..., description="User answer(s)")


class AssessmentBulkSubmitRequest(BaseSchema):
    """Request to submit multiple assessment answers at once (optional future use)."""
    session_id: str
    answers: List[dict]
