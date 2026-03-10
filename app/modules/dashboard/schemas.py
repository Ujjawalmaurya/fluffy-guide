"""Dashboard schemas."""
from pydantic import BaseModel
from typing import Optional


class JobMatchOut(BaseModel):
    id: str
    title: str
    company: str
    location_city: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    required_skills: Optional[list[str]]


class DashboardSummary(BaseModel):
    user: dict
    profile_completion_pct: int
    onboarding_done: bool
    quick_assessment_done: bool  # always False in MVP
    gap_analysis_done: bool      # always False in MVP
    extracted_skills: list[str]
    career_interests: list[str]
    location: dict
    job_matches: list[dict]
