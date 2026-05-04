from typing import Optional, List
from app.schemas.base import BaseSchema

class ResourceResponse(BaseSchema):
    id: str
    name: str
    provider: str
    url: str
    description: Optional[str] = None
    skill_tags: List[str]
    category: str
    is_free: bool
    cost_inr: int
    duration_weeks: Optional[int] = None
    difficulty_level: Optional[int] = None
    language: str
    delivery_type: Optional[str] = None
    is_active: bool
    created_at: str

class BulkUploadResponse(BaseSchema):
    created: int
    failed: int
    message: str = "Bulk upload completed"
