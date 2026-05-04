"""
LLM Input Schemas
Lean, prompt-ready models for LLM calls.
"""
from typing import List, Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class CareerGuidanceLLMInput(BaseSchema):
    """Context for career guidance prompts."""
    name: str
    user_type: str
    state: str
    education_level: str
    skills: List[str]
    interests: List[str]
    goal: Optional[str] = None

    def to_prompt_str(self) -> str:
        """Converts model to a clean string for prompts."""
        return (
            f"User: {self.name} ({self.user_type})\n"
            f"Location: {self.state}\n"
            f"Education: {self.education_level}\n"
            f"Current Skills: {', '.join(self.skills)}\n"
            f"Interests: {', '.join(self.interests)}\n"
            f"Stated Goal: {self.goal or 'Discovering paths'}"
        )


class ResumeAnalysisLLMInput(BaseSchema):
    """Context for resume analysis prompts."""
    resume_text: str
    target_role: Optional[str] = None

    def to_prompt_str(self) -> str:
        return f"Resume Content:\n{self.resume_text}\n\nTarget Role: {self.target_role or 'Not specified'}"


class MockInterviewLLMInput(BaseSchema):
    """Context for mock interview prompts."""
    role: str
    difficulty: str = "medium"
    history: List[dict] = []  # Previous Q&A pairs

    def to_prompt_str(self) -> str:
        history_str = "\n".join([f"Q: {h['q']}\nA: {h['a']}" for h in self.history])
        return f"Role: {self.role}\nDifficulty: {self.difficulty}\nPrevious Interaction:\n{history_str}"


class RoadmapGenerationLLMInput(BaseSchema):
    """Context for roadmap generation prompts."""
    skill_gaps: List[str]
    target_role: str
    timeframe: str = "12 weeks"

    def to_prompt_str(self) -> str:
        return f"Gaps: {', '.join(self.skill_gaps)}\nTarget: {self.target_role}\nDuration: {self.timeframe}"
