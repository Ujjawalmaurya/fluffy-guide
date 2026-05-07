"""
User Request Schemas
Handles registration and profile updates.
"""
from typing import Optional, List
from pydantic import EmailStr, Field, field_validator
from app.schemas.base import BaseSchema
from app.schemas.enums import CareerStage, EducationLevel, Language, Gender, Region


class UserCreateRequest(BaseSchema):
    """Registration request for new users."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    career_stage: CareerStage
    preferred_lang: Language = Language.ENGLISH

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "full_name": "Raj Kumar",
                "career_stage": "fresher",
                "preferred_lang": "hindi"
            }
        }
    )


class UserProfileUpdateRequest(BaseSchema):
    """Profile edit request."""
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=15, le=100)
    gender: Optional[Gender] = None
    state: Optional[Region] = None
    city: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    languages: Optional[List[Language]] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "full_name": "Raj Kumar",
                "age": 22,
                "education_level": "graduate",
                "state": "Maharashtra"
            }
        }
    )


class UserSkillsUpdateRequest(BaseSchema):
    """Skill list update request."""
    skills: List[str]
    interests: List[str]

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "skills": ["python", "data entry", "excel"],
                "interests": ["software development", "banking"]
            }
        }
    )
