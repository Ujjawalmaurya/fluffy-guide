"""
rate_limiter.py — Rate limiting for LLM bullet improvement calls.
"""
from datetime import datetime, date
from app.core.config import settings


async def check_bullet_rate_limit(user_id: str, db) -> bool:
    """Checks and updates the daily rate limit for bullet improvements."""
    now = datetime.now()
    today = date.today()

    result = db.table("user_rate_limits").select("*").eq("user_id", user_id).execute()

    if not result.data:
        db.table("user_rate_limits").insert({
            "user_id": user_id,
            "bullet_improvement_count": 0,
            "last_reset_at": now.isoformat(),
        }).execute()
        return True

    record = result.data[0]
    last_reset = datetime.fromisoformat(record["last_reset_at"].replace("Z", "+00:00")).date()
    count = record["bullet_improvement_count"]

    if last_reset < today:
        db.table("user_rate_limits").update({
            "bullet_improvement_count": 0,
            "last_reset_at": now.isoformat(),
        }).eq("user_id", user_id).execute()
        return True

    return count < settings.resume_bullet_daily_limit


async def increment_bullet_rate_limit(user_id: str, db):
    """Increments the daily bullet improvement count for the user."""
    res = db.table("user_rate_limits").select("bullet_improvement_count").eq("user_id", user_id).single().execute()
    current_count = res.data["bullet_improvement_count"] if res.data else 0

    db.table("user_rate_limits").update({
        "bullet_improvement_count": current_count + 1,
        "updated_at": "now()",
    }).eq("user_id", user_id).execute()
