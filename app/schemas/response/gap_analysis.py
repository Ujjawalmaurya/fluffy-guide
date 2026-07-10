"""
Gap Analysis Response Schemas
Results from comparing user skills to market needs.
"""
from typing import List, Optional, Any
from app.schemas.base import BaseSchema


class StrengthItem(BaseSchema):
    skill_name: str
    proficiency_label: str
    job_demand_pct: float
    message: str


class GapItem(BaseSchema):
    skill_name: str
    category: str
    priority_score: float
    frequency_pct: float
    learnability_weeks: int
    recommended_resources: List[Any] = []


class PartialMatch(BaseSchema):
    skill_name: str
    current_level: int
    current_label: str
    required_level: int
    gap_size: int


class RoadmapWeek(BaseSchema):
    week: int
    focus_skill: str
    goal: str
    action: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    resource_url: Optional[str] = None
    milestone: str


class GapAnalysisReportResponse(BaseSchema):
    """Full gap analysis report."""
    id: Optional[str] = None
    user_id: str
    profile_hash: Optional[str] = None
    strengths: List[StrengthItem] = []
    gaps: List[GapItem] = []
    partial_matches: List[PartialMatch] = []
    roadmap: List[RoadmapWeek] = []
    total_jobs_analyzed: int = 0
    is_stale: bool = False
    computed_at: str
    created_at: Optional[str] = None
    from_cache: bool = False
    motivational_note: Optional[str] = None

