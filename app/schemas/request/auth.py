"""
Authentication Request Schemas
Handles login, registration, and session management.
"""
from pydantic import EmailStr, Field
from app.schemas.base import BaseSchema
from app.schemas.enums import UserRole


class OTPRequest(BaseSchema):
    """Request a one-time password."""
    email: EmailStr

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "email": "user@example.com"
            }
        }
    )


class SignupRequest(BaseSchema):
    """Initial signup with role selection."""
    email: EmailStr
    role: UserRole

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "role": "individual_youth"
            }
        }
    )


class OTPVerifyRequest(BaseSchema):
    """Verify OTP and get tokens."""
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=6)

    model_config = BaseSchema.get_config(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "otp": "123456"
            }
        }
    )


class TokenRefreshRequest(BaseSchema):
    """Request new access token using refresh token."""
    refresh_token: str
