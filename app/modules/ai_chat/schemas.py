"""AI chat module schemas."""
from pydantic import BaseModel
from typing import Optional


class ChatMessageIn(BaseModel):
    content: str
    language: str = "en"  # 'en' or 'hi'


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    language: str
    created_at: str
