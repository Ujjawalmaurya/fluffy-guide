"""
AI Chat Response Schemas
Handles history and individual messages from the AI assistant.
"""
from datetime import datetime

from app.schemas.base import BaseSchema
from app.schemas.enums import Language


class ChatMessageResponse(BaseSchema):
    """A single chat message in history."""
    id: str
    role: str
    content: str
    language: Language
    created_at: datetime

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "id": "msg_123",
                "role": "assistant",
                "content": "You can start by learning SEO and SEM basics.",
                "language": "english",
                "created_at": "2024-05-01T10:00:00Z"
            }
        }
    )
