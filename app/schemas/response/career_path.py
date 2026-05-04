"""
Career Path Response Schemas
Recommendations and week-by-week roadmaps.
"""
from typing import List, Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class RecommendedRole(BaseSchema):
    """Specific role recommendation."""
    role_name: str
    reasoning: str
    confidence_score: float = Field(..., ge=0, le=1)
    salary_range_est: Optional[str] = None


class CareerPathResponse(BaseSchema):
    """List of recommended career paths."""
    recommended_roles: List[RecommendedRole]
    next_steps: List[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "recommended_roles": [
                    {
                        "role_name": "Solar Technician",
                        "reasoning": "Fits your interest in mechanical work and local market demand.",
                        "confidence_score": 0.9
                    }
                ],
                "next_steps": ["Take a basic electrical safety quiz", "Look for local training centers"]
            }
        }
    }


class RoadmapStep(BaseSchema):
    """Weekly step in a learning roadmap."""
    week: int
    focus_skill: str
    goal: str
    action: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    resource_url: Optional[str] = None
    milestone: str


class RoadmapResponse(BaseSchema):
    """Complete week-by-week roadmap."""
    total_weeks: int
    weekly_commitment_hours: int
    roadmap: List[RoadmapStep]
    motivational_note: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_weeks": 4,
                "weekly_commitment_hours": 10,
                "roadmap": [
                    {
                        "week": 1,
                        "focus_skill": "Safety",
                        "goal": "Understand shop safety",
                        "action": "Watch the intro video",
                        "milestone": "Pass the safety quiz"
                    }
                ],
                "motivational_note": "You are making great progress!"
            }
        }
    }
