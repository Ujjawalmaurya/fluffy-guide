from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserType

class UserBase(BaseModel):
    email: EmailStr
    user_type: UserType

class UserCreate(UserBase):
    password: Optional[str] = None # No password for OAuth

class RoleSelection(BaseModel):
    user_type: UserType
    # Fields based on type
    full_name: Optional[str] = None
    career_goals: Optional[str] = None
    org_name: Optional[str] = None
    org_type: Optional[str] = None

class EndUserCreate(UserCreate):
    full_name: str
    career_goals: Optional[str] = None

class OrgCreate(UserCreate):
    org_name: str
    org_type: str # NGO, Training, Employer

class UserOut(BaseModel):
    id: int
    email: EmailStr
    user_type: Optional[UserType] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_type: Optional[UserType] = None
