"""
User Database Schemas
Full document shapes for MongoDB/PostgreSQL.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import EmailStr, Field
from app.schemas.base import BaseSchema


class UserTrainingRecord(BaseSchema):
    """Record of a user's training enrollment."""
    course_id: str
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "in_progress"
    progress_percentage: int = 0
    completion_date: Optional[datetime] = None
    outcome: Optional[str] = None


class UserDocument(BaseSchema):
    """Full user document in the database."""
    id: str
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    onboarding_done: bool = False
    onboarding_step: int = 0
    profile_complete_pct: int = 0
    training_history: List[UserTrainingRecord] = []
    metadata: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
