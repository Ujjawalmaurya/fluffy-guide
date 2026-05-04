"""
Profile Response Schemas
User profile data and analysis results.
"""
from typing import Optional, List, Dict, Any
from app.schemas.base import BaseSchema
from app.schemas.enums import EducationLevel, Language


class ProfileResponse(BaseSchema):
    """Detailed user profile information."""
    id: str
    user_id: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    languages: Optional[List[Language]] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class ParsedResumeResponse(BaseSchema):
    """Structured data extracted from a resume."""
    skills_found: List[Dict[str, Any]]
    education_hints: List[Dict[str, Any]]
    experience_hints: List[Dict[str, Any]]
    experience_level: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    career_suggestions: Optional[List[str]] = None
    skill_gap_analysis: Optional[str] = None


class CompletionScoreResponse(BaseSchema):
    """Profile completeness analysis."""
    score: int
    filled_fields: List[str]
    missing_fields: List[str]
