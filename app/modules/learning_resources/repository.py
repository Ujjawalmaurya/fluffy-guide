# [LEARNING_RESOURCES] DB queries only. No business logic.
from app.core.database import get_supabase
from app.core.logger import get_logger

logger = get_logger("LEARNING_RESOURCES")

async def find_by_skill_tag(tag: str, limit: int = 5) -> list:
    """
    Finds active resources where skill_tags contains the given tag.
    Uses PostgreSQL array containment. Case-insensitive match.
    """
    supabase = get_supabase()
    result = (
        supabase.table("learning_resources")
        .select("*")
        .contains("skill_tags", [tag.lower()])
        .eq("is_active", True)
        .limit(limit)
        .execute()
    )
    return result.data or []

async def get_all_filtered(
    category: str = None,
    is_free: bool = None,
    language: str = None,
    skill_tag: str = None
) -> list:
    supabase = get_supabase()
    query = (
        supabase.table("learning_resources")
        .select("*")
        .eq("is_active", True)
    )
    
    if category:
        query = query.eq("category", category)
    if is_free is not None:
        query = query.eq("is_free", is_free)
    if language:
        query = query.eq("language", language)
    if skill_tag:
        query = query.contains("skill_tags", [skill_tag.lower()])
        
    return query.execute().data or []

async def get_by_id(resource_id: str) -> dict | None:
    supabase = get_supabase()
    result = (
        supabase.table("learning_resources")
        .select("*")
        .eq("id", resource_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

async def create(data: dict) -> dict:
    supabase = get_supabase()
    result = supabase.table("learning_resources").insert(data).execute()
    logger.info(f"[LEARNING_RESOURCES] Created: {data.get('name')}")
    return result.data[0]

async def update(resource_id: str, data: dict) -> dict:
    supabase = get_supabase()
    result = (
        supabase.table("learning_resources")
        .update(data)
        .eq("id", resource_id)
        .execute()
    )
    return result.data[0]

async def soft_delete(resource_id: str) -> bool:
    supabase = get_supabase()
    supabase.table("learning_resources").update(
        {"is_active": False}
    ).eq("id", resource_id).execute()
    logger.info(f"[LEARNING_RESOURCES] Soft deleted: {resource_id}")
    return True

async def bulk_create(items: list[dict]) -> dict:
    supabase = get_supabase()
    created, failed = 0, 0
    for item in items:
        try:
            supabase.table("learning_resources").insert(item).execute()
            created += 1
        except Exception as e:
            logger.error(f"[LEARNING_RESOURCES] Bulk insert failed: {e}")
            failed += 1
            
    logger.info(
        f"[LEARNING_RESOURCES] Bulk upload done. "
        f"created={created} failed={failed}"
    )
    return {"created": created, "failed": failed}
