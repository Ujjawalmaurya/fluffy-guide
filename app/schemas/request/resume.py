"""
Resume Request Schemas
Handles resume analysis and improvement requests.
"""
from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class ResumeAnalysisRequest(BaseSchema):
    """Raw resume text analysis request."""
    resume_text: str = Field(..., min_length=50)
    target_role: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_text": "Experience in web development using React and Node.js...",
                "target_role": "Senior Frontend Engineer"
            }
        }
    }


class ResumeImproveRequest(BaseSchema):
    """Resume improvement request based on target job."""
    resume_text: str
    target_job_id: Optional[str] = None
    target_role: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_text": "I worked as a clerk for 2 years...",
                "target_role": "Administrative Assistant"
            }
        }
    }
