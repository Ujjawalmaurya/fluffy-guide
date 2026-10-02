"""
schemas.py — Request and response models for demo authentication.
"""
from typing import Dict, Any
from pydantic import BaseModel


class DemoLoginRequest(BaseModel):
    persona: str  # 'ravi' | 'meera' | 'arjun' | 'admin'


class DemoUserResponse(BaseModel):
    id: str
    email: str
    user_type: str
    preferred_lang: str = "en"
    onboarding_done: bool = True
    full_name: str


class DemoLoginData(BaseModel):
    persona: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: DemoUserResponse


class DemoLoginResponse(BaseModel):
    success: bool
    data: DemoLoginData
