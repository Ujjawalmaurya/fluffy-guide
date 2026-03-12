from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID

class SkillItem(BaseModel):
    skill_name: str
    category: str
    proficiency_numeric: int
    proficiency_label: str
    source: str
    confidence_score: float
    last_updated: datetime

class UserSkillProfile(BaseModel):
    user_id: UUID
    skills: List[SkillItem]
    profile_version: int
    resume_contributed: bool
    assessment_contributed: bool
    updated_at: datetime

class SkillSummary(BaseModel):
    total_skills: int
    by_category: Dict[str, List[SkillItem]]
    top_5: List[SkillItem]
    source_breakdown: dict
