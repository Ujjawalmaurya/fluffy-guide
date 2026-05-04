"""
Authentication Response Schemas
Safe public fields and session tokens.
"""
from typing import Optional
from pydantic import EmailStr
from app.schemas.base import BaseSchema
from app.schemas.enums import UserRole


class TokenResponse(BaseSchema):
    """Access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserAuthResponse(BaseSchema):
    """User info returned after authentication."""
    id: str
    email: EmailStr
    role: Optional[UserRole] = None
    user_type: Optional[str] = None
    onboarding_done: bool = False
    onboarding_step: int = 0
    profile_complete_percentage: int = 0
    preferred_lang: str
    is_active: bool
    created_at: str
