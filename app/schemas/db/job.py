"""
Job Database Schemas
Shapes for job listings in the DB.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import Field
from app.schemas.base import BaseSchema


class JobDocument(BaseSchema):
    """Full job listing document."""
    id: str
    title: str
    company: str
    description: str
    location_city: str
    location_state: str
    skills_required: List[str]
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    source: str = "internal"
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: dict = {}

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "job_999",
                "title": "Junior Electrician",
                "company": "Tata Power",
                "location_city": "Nagpur",
                "skills_required": ["Wiring", "Safety"],
                "scraped_at": "2024-01-01T00:00:00Z"
            }
        }
    }
