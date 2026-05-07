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

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "id": "user_123",
                "email": "raj@example.com",
                "full_name": "Raj Kumar",
                "career_stage": "fresher",
                "onboarding_done": True,
                "profile_complete_percentage": 85
            }
        }
    )


class UserDashboardResponse(BaseSchema):
    """Dashboard summary for the user."""
    profile: UserProfileResponse
    ai_highlight: Optional[str] = None
    job_matches: List[dict] = []
    recommended_courses: List[dict] = []
    role_specific: Optional[dict] = None
    show_assessment_nudge: bool = False
    primary_role: Optional[str] = None
    experience_years: Optional[int] = None
    extracted_skills: List[dict] = []
    quick_assessment_done: bool = False
    recent_activity: List[dict] = []
    
    progress_summary: dict = {
        "courses_completed": 0,
        "assessments_taken": 0,
        "skills_verified": 0
    }
    notifications_count: int = 0

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "profile": {
                    "id": "user_123",
                    "email": "raj@example.com",
                    "full_name": "Raj Kumar",
                    "career_stage": "student",
                    "onboarding_done": True,
                    "profile_complete_percentage": 85,
                    "languages": ["english"]
                },
                "ai_highlight": "Focus on Python to unlock 5 new roles.",
                "job_matches": [],
                "progress_summary": {
                    "courses_completed": 2,
                    "assessments_taken": 1,
                    "skills_verified": 3
                },
                "notifications_count": 0
            }
        }
    )
