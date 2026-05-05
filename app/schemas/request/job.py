"""
Job Request Schemas
Handles job creation, searching, and matching.
"""
from typing import Optional, List
from pydantic import Field
from app.schemas.base import BaseSchema
from app.schemas.enums import JobType, WorkMode


class JobCreateRequest(BaseSchema):
    """Request to create a new job listing."""
    title: str
    company: Optional[str] = None
    description: Optional[str] = None
    location_state: Optional[str] = Field(None, validation_alias="location")
    location_city: Optional[str] = None
    job_type: Optional[JobType] = Field(None, validation_alias="type")
    work_mode: Optional[WorkMode] = None
    category: Optional[str] = None
    required_skills: List[str] = []
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_min: Optional[int] = None
    source_url: Optional[str] = None

    # Extra field to catch raw salary from frontend
    salary: Optional[str] = None


class JobUpdateRequest(BaseSchema):
    """Request to update an existing job listing."""
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location_state: Optional[str] = None
    location_city: Optional[str] = None
    job_type: Optional[JobType] = None
    work_mode: Optional[WorkMode] = None
    category: Optional[str] = None
    required_skills: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_min: Optional[int] = None
    source_url: Optional[str] = None
    is_active: Optional[bool] = None


class JobFilterRequest(BaseSchema):
    """Filters for job listing queries."""
    state: Optional[str] = None
    category: Optional[str] = None
    job_type: Optional[JobType] = None
    query: Optional[str] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class JobSearchRequest(BaseSchema):
    """Request for AI-powered job search/matching."""
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    work_mode: Optional[WorkMode] = None
    skills: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "delivery partner",
                "location": "bengaluru",
                "job_type": "gig"
            }
        }
    }


class JobMatchRequest(BaseSchema):
    """Request to match user profile against jobs."""
    user_id: str
    limit: int = Field(10, ge=1, le=50)

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "limit": 5
            }
        }
    }
