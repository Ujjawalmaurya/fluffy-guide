"""
Job Match Response Schemas
Matches between user and available jobs.
"""
from typing import List, Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class JobMatchDetail(BaseSchema):
    """Specific job match information."""
    job_id: str
    title: str
    company: str
    location: str
    match_score: float = Field(..., ge=0, le=1)
    missing_skills: List[str]
    salary_est: Optional[str] = None
    apply_url: Optional[str] = None


class JobMatchResponse(BaseSchema):
    """List of matched jobs for a user."""
    matches: List[JobMatchDetail]
    count: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "matches": [
                    {
                        "job_id": "job_789",
                        "title": "Delivery Executive",
                        "company": "Swiggy",
                        "location": "Mumbai",
                        "match_score": 0.95,
                        "missing_skills": []
                    }
                ],
                "count": 1
            }
        }
    }
