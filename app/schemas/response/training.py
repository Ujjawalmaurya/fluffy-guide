"""
Training Response Schemas
Course and training recommendations.
"""
from typing import List, Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class TrainingRecommendation(BaseSchema):
    """Specific course or training recommendation."""
    course_id: str
    title: str
    provider: str
    cost: float = 0.0
    currency: str = "INR"
    duration: str
    relevance_score: float = Field(..., ge=0, le=1)
    description: Optional[str] = None
    url: Optional[str] = None


class TrainingRecommendationResponse(BaseSchema):
    """List of training recommendations."""
    recommendations: List[TrainingRecommendation]

    model_config = {
        "json_schema_extra": {
            "example": {
                "recommendations": [
                    {
                        "course_id": "course_abc",
                        "title": "Excel for Beginners",
                        "provider": "Skill India",
                        "cost": 0.0,
                        "duration": "2 weeks",
                        "relevance_score": 0.98
                    }
                ]
            }
        }
    }
