"""
schemas.py — Request and response models for mock interviews.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class StartRequest(BaseModel):
    target_role: str
    skills: List[str] = []
    question_count: int = 5


class AnswerRequest(BaseModel):
    session_id: str
    question_id: int
    answer: str
