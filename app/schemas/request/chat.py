"""
AI Chat Request Schemas
Handles messages sent to the AI assistant.
"""
from typing import Optional
from app.schemas.base import BaseSchema
from app.schemas.enums import Language


class ChatRequest(BaseSchema):
    """Request message for AI chat."""
    content: str
    language: Language = Language.ENGLISH

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": "How can I become a digital marketing expert?",
                "language": "english"
            }
        }
    }
