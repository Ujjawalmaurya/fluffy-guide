"""
Gap Analysis Response Schemas
Results from comparing user skills to market needs.
"""
from typing import List, Optional, Dict, Any
from app.schemas.base import BaseSchema
from app.schemas.enums import SkillLevel


class SkillGapItem(BaseSchema):
    """Specific skill gap identified."""
    skill_name: str
    current_level: Optional[SkillLevel] = None
    required_level: SkillLevel
    importance: float = 1.0  # 0 to 1
    description: str


class RoadmapStep(BaseSchema):
    """Single step in a learning roadmap."""
    order: int
    title: str
    description: str
    estimated_duration: str
    resources: List[str] = []


class GapAnalysisReportResponse(BaseSchema):
    """Full gap analysis report."""
    user_id: str
    target_role: str
    overall_match_score: float = 0.0
    gaps: List[SkillGapItem]
    roadmap: List[RoadmapStep]
    motivational_note: Optional[str] = None
    created_at: str
    from_cache: bool = False
