from typing import Optional, List
from app.schemas.base import BaseSchema

class ResourceCreateRequest(BaseSchema):
    name: str
    provider: str
    url: str
    description: Optional[str] = None
    skill_tags: List[str]
    category: str
    is_free: bool = True
    cost_inr: int = 0
    duration_weeks: Optional[int] = None
    difficulty_level: Optional[int] = None
    language: str = "en"
    delivery_type: Optional[str] = None

class ResourceUpdateRequest(BaseSchema):
    name: Optional[str] = None
    provider: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    skill_tags: Optional[List[str]] = None
    category: Optional[str] = None
    is_free: Optional[bool] = None
    cost_inr: Optional[int] = None
    duration_weeks: Optional[int] = None
    difficulty_level: Optional[int] = None
    language: Optional[str] = None
    delivery_type: Optional[str] = None
    is_active: Optional[bool] = None
