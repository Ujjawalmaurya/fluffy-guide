"""
Skill Gap Response Schemas
Analyzed gaps between user and target roles.
"""
from typing import List
from app.schemas.base import BaseSchema


class GapItem(BaseSchema):
    """Specific skill gap detail."""
    skill_name: str
    priority: int = 1  # 1 (high) to 3 (low)
    current_level: str = "none"
    target_level: str = "intermediate"
    reason: str


class SkillGapResponse(BaseSchema):
    """Full skill gap analysis result."""
    target_role: str
    required_skills: List[str]
    current_skills: List[str]
    gaps: List[GapItem]
    priority_order: List[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "target_role": "Data Entry Operator",
                "required_skills": ["Excel", "Typing", "Communication"],
                "current_skills": ["Communication"],
                "gaps": [
                    {"skill_name": "Excel", "priority": 1, "reason": "Essential for job"},
                    {"skill_name": "Typing", "priority": 2, "reason": "Speed needs improvement"}
                ],
                "priority_order": ["Excel", "Typing"]
            }
        }
    }
