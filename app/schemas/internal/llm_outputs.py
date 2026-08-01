"""
LLM Output Schemas
Parsed and validated models from LLM responses.
"""
from typing import List, Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class CareerGuidanceLLMOutput(BaseSchema):
    """
    Parsed output for career guidance.
    Retry policy: 2 retries on JSON parse failure.
    """
    recommended_roles: List[str] = Field(default_factory=list)
    reasoning: str = "Guidance based on current skills and interests."
    next_steps: List[str] = Field(default_factory=list)


class ResumeAnalysisLLMOutput(BaseSchema):
    """
    Parsed output for resume analysis.
    Retry policy: 2 retries on missing mandatory fields.
    """
    score: int = 0
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class RoadmapStepLLM(BaseSchema):
    """Weekly step in roadmap as produced by LLM."""
    week: int
    focus_skill: str
    goal: str
    action: str
    milestone: str


class RoadmapLLMOutput(BaseSchema):
    """
    Parsed output for learning roadmaps.
    Retry policy: 1 retry with reduced week count if failed.
    """
    total_weeks: int = 0
    weekly_commitment_hours: int = 0
    roadmap: List[RoadmapStepLLM] = Field(default_factory=list)
    motivational_note: str = "Keep moving forward!"


class AssessmentQuestionLLMOutput(BaseSchema):
    """
    Parsed output for a single assessment question within a batch.
    """
    question: str
    question_type: str = "mcq" # Defaulting to mcq for chips
    options: List[str] = Field(default_factory=list) # Options are now required for chips
    allows_multiple: bool = False
    allows_other: bool = True
    skill_probing: str = "general"

class AssessmentBatchLLMOutput(BaseSchema):
    """
    Parsed output for a batch of assessment questions.
    """
    questions: List[AssessmentQuestionLLMOutput]
    phase: int
    phase_name: str


class SkillExtractionLLMOutput(BaseSchema):
    """
    Parsed output for skill extraction from session.
    """
    skills: List[dict] = Field(default_factory=list)
    career_goals: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    work_preferences: dict = Field(default_factory=dict)
    assessment_summary: str = "Assessment completed."
