"""Auth module — Pydantic schemas for request/response models."""
from pydantic import BaseModel, EmailStr


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    email: str
    user_type: str | None
    preferred_lang: str
    is_active: bool
    onboarding_done: bool
    created_at: str
