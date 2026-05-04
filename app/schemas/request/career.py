"""
Career Request Schemas
Handles career guidance and roadmap generation.
"""
from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class CareerGuidanceRequest(BaseSchema):
    """Request for AI career guidance."""
    career_goal: Optional[str] = None
    timeframe_months: int = Field(12, ge=1, le=60)

    model_config = {
        "json_schema_extra": {
            "example": {
                "career_goal": "Want to become a Solar Technician",
                "timeframe_months": 6
            }
        }
    }


class RoadmapRequest(BaseSchema):
    """Request for a week-by-week learning roadmap."""
    target_role: str
    current_skills: list[str]
    timeframe_weeks: int = Field(12, ge=4, le=24)

    model_config = {
        "json_schema_extra": {
            "example": {
                "target_role": "Electrician",
                "current_skills": ["Basic math", "Manual labor"],
                "timeframe_weeks": 8
            }
        }
    }
