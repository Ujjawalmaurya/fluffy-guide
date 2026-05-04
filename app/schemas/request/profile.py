"""
Profile Request Schemas
Handles profile updates and information gathering.
"""
from typing import Optional, List
from pydantic import Field
from app.schemas.base import BaseSchema
from app.schemas.enums import EducationLevel, Language


class ProfileUpdateRequest(BaseSchema):
    """Generic profile update request."""
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=14, le=100)
    gender: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    languages: Optional[List[Language]] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "Raj Kumar",
                "age": 22,
                "education_level": "graduate",
                "state": "Maharashtra"
            }
        }
    }


class UserSkillsUpdateRequest(BaseSchema):
    """Update user skills and interests."""
    skills: List[str]
    interests: List[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "skills": ["python", "excel"],
                "interests": ["data science", "finance"]
            }
        }
    }
