# [GAP_ANALYSIS] DB queries only.

from app.core.database import get_async_supabase

async def get_by_user_id(user_id: str) -> dict | None:
    db = await get_async_supabase()
    result = await (
        db.table("gap_analysis_reports")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

async def upsert(user_id: str, data: dict) -> dict:
    db = await get_async_supabase()
    existing = await get_by_user_id(user_id)
    if existing:
        result = await (
            db.table("gap_analysis_reports")
            .update(data)
            .eq("user_id", user_id)
            .execute()
        )
    else:
        result = await (
            db.table("gap_analysis_reports")
            .insert({"user_id": user_id, **data})
            .execute()
        )
    return result.data[0] if result.data else {}

async def mark_stale(user_id: str) -> None:
    db = await get_async_supabase()
    await db.table("gap_analysis_reports").update(
        {"is_stale": True}
    ).eq("user_id", user_id).execute()


