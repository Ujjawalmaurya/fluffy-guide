"""
Skill Profile Response Schemas
Detailed skill sets, proficiencies, and summaries.
"""
from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID
from app.schemas.base import BaseSchema


class SkillItemResponse(BaseSchema):
    """A single skill entry."""
    skill_name: str
    category: str
    proficiency_numeric: int
    proficiency_label: str
    source: str
    confidence_score: float
    last_updated: datetime


class SkillProfileResponse(BaseSchema):
    """Full skill profile for a user."""
    user_id: UUID
    skills: List[SkillItemResponse]
    profile_version: int
    resume_contributed: bool
    assessment_contributed: bool
    updated_at: datetime


class SkillSummaryResponse(BaseSchema):
    """High-level summary of a user's skills."""
    total_skills: int
    by_category: Dict[str, List[SkillItemResponse]]
    top_5: List[SkillItemResponse]
    source_breakdown: Dict[str, int]
