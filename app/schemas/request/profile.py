"""
Profile Request Schemas
Handles profile updates and information gathering.
"""
from typing import Optional, List, Any
from pydantic import Field, field_validator
from app.schemas.base import BaseSchema
from app.schemas.enums import EducationLevel, Language, Gender, Region


class ProfileUpdateRequest(BaseSchema):
    """Generic profile update request."""
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=14, le=100)
    gender: Optional[Gender] = None
    state: Optional[Region] = None
    city: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    languages: Optional[List[Language]] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    interests: Optional[List[str]] = None
    secondary_skills: Optional[List[str]] = None


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
    """Update user skills and interests."""
    skills: List[str]
    interests: List[str]

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "skills": ["python", "excel"],
                "interests": ["data science", "finance"]
            }
        }
    )
