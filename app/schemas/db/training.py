"""
Training Database Schemas
Shapes for course catalog in the DB.
"""
from typing import List, Optional
from app.schemas.base import BaseSchema


class TrainingDocument(BaseSchema):
    """Course catalog entry."""
    id: str
    title: str
    provider: str
    skill_tags: List[str]
    duration_hours: float
    difficulty: str
    cost_inr: float = 0.0
    url: str
    description: Optional[str] = None
