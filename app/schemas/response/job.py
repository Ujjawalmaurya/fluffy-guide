"""
Job Response Schemas
Safe public fields for job listings.
"""
from typing import Optional, List
from app.schemas.base import BaseSchema
from app.schemas.enums import JobType, WorkMode


class JobResponse(BaseSchema):
    """Full job listing information."""
    id: str
    title: str
    company: str
    description: Optional[str] = None
    location_state: str
    location_city: Optional[str] = None
    job_type: Optional[JobType] = None
    work_mode: Optional[WorkMode] = None
    category: str
    required_skills: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_min: Optional[int] = None
    source_url: Optional[str] = None
    is_active: bool
