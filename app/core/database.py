"""
Supabase client singleton. One connection, shared across the app.
Tested on startup — fail fast if creds are wrong.
"""
from supabase import create_client, Client
from app.core.config import settings
from app.core.logger import get_logger

log = get_logger("DATABASE")

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
        log.debug("Supabase client created")
    return _client


def test_connection() -> bool:
    """Quick connectivity check — called at startup."""
    try:
        db = get_supabase()
        # Lightest possible query: just check the users table exists
        db.table("users").select("id").limit(1).execute()
        log.info("Supabase connection OK")
        return True
    except Exception as e:
        log.error(f"Supabase connection FAILED: {e}")
        return False
