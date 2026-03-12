# [LEARNING_RESOURCES] Public GET endpoints + admin CRUD.
# Admin routes protected by X-Admin-Secret header.

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional
from app.modules.learning_resources import repository
from app.modules.learning_resources.schemas import (
    ResourceCreate, ResourceUpdate
)
from app.shared.response_models import APIResponse
from app.core.config import settings as get_settings
from app.core.logger import get_logger

logger = get_logger("LEARNING_RESOURCES_ROUTER")
router = APIRouter(prefix="/learning-resources", tags=["Learning Resources"])

def _verify_admin(x_admin_secret: str = Header(None)):
    settings = get_settings
    if x_admin_secret != settings.admin_secret:
        logger.warning("[LEARNING_RESOURCES] Unauthorized admin attempt")
        raise HTTPException(status_code=403, detail={
            "success": False,
            "error_code": "ADMIN_UNAUTHORIZED",
            "message": "Invalid admin secret."
        })

@router.get("/", response_model=APIResponse)
async def list_resources(
    category: Optional[str] = Query(None),
    is_free: Optional[bool] = Query(None),
    language: Optional[str] = Query(None),
    skill_tag: Optional[str] = Query(None)
):
    """Public endpoint — returns active resources with optional filters."""
    resources = await repository.get_all_filtered(
        category, is_free, language, skill_tag
    )
    return APIResponse(success=True, data=resources)

@router.get("/{resource_id}", response_model=APIResponse)
async def get_resource(resource_id: str):
    resource = await repository.get_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail={
            "success": False, "error_code": "RESOURCE_NOT_FOUND",
            "message": "Resource not found."
        })
    return APIResponse(success=True, data=resource)

@router.post("/admin/create", response_model=APIResponse)
async def admin_create(
    body: ResourceCreate,
    x_admin_secret: str = Header(None)
):
    _verify_admin(x_admin_secret)
    resource = await repository.create(body.model_dump())
    return APIResponse(success=True, data=resource)

@router.patch("/admin/{resource_id}", response_model=APIResponse)
async def admin_update(
    resource_id: str,
    body: ResourceUpdate,
    x_admin_secret: str = Header(None)
):
    _verify_admin(x_admin_secret)
    data = body.model_dump(exclude_none=True)
    resource = await repository.update(resource_id, data)
    return APIResponse(success=True, data=resource)

@router.delete("/admin/{resource_id}", response_model=APIResponse)
async def admin_delete(
    resource_id: str,
    x_admin_secret: str = Header(None)
):
    _verify_admin(x_admin_secret)
    await repository.soft_delete(resource_id)
    return APIResponse(success=True, data={"deleted": True})

@router.post("/admin/bulk", response_model=APIResponse)
async def admin_bulk_upload(
    items: list[ResourceCreate],
    x_admin_secret: str = Header(None)
):
    _verify_admin(x_admin_secret)
    result = await repository.bulk_create(
        [i.model_dump() for i in items]
    )
    return APIResponse(success=True, data=result)
