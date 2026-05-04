"""
User Response Schemas
Safe public fields and dashboard summaries.
"""
from typing import Optional, List, Any
from pydantic import EmailStr
from app.schemas.base import BaseSchema
from app.schemas.enums import CareerStage, EducationLevel, Language


class UserProfileResponse(BaseSchema):
    """Public profile information."""
    id: str
    email: EmailStr
    full_name: Optional[str]
    career_stage: CareerStage
    age: Optional[int]
    gender: Optional[str]
    state: Optional[str]
    city: Optional[str]
    education_level: Optional[EducationLevel]
    languages: List[Language]
    avatar_url: Optional[str]
    onboarding_done: bool
    profile_complete_percentage: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "user_123",
                "email": "raj@example.com",
                "full_name": "Raj Kumar",
                "career_stage": "fresher",
                "onboarding_done": True,
                "profile_complete_percentage": 85
            }
        }
    }


class UserDashboardResponse(BaseSchema):
    """Dashboard summary for the user."""
    profile: UserProfileResponse
    progress_summary: dict = {
        "courses_completed": 0,
        "assessments_taken": 0,
        "skills_verified": 0
    }
    top_recommendations: List[dict]
    notifications_count: int = 0

    model_config = {
        "json_schema_extra": {
            "example": {
                "profile": {
                    "id": "user_123",
                    "email": "raj@example.com",
                    "full_name": "Raj Kumar",
                    "career_stage": "fresher",
                    "onboarding_done": True,
                    "profile_complete_percentage": 85,
                    "languages": ["english"]
                },
                "progress_summary": {
                    "courses_completed": 2,
                    "assessments_taken": 1
                },
                "top_recommendations": []
            }
        }
    }
