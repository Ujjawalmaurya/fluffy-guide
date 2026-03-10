"""Profile repository — all DB queries for profile and enrichment tables."""
from supabase import Client
from app.core.logger import get_logger

log = get_logger("PROFILE")


class ProfileRepository:
    def __init__(self, db: Client):
        self.db = db

    def get_profile(self, user_id: str) -> dict | None:
        result = self.db.table("user_profiles").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    def update_profile(self, user_id: str, data: dict):
        # Filter out None values — don't overwrite existing data with None
        clean = {k: v for k, v in data.items() if v is not None}
        if not clean:
            return
        result = self.db.table("user_profiles") \
            .update(clean) \
            .eq("user_id", user_id) \
            .execute()
        return result.data[0] if result.data else None

    def upsert_enrichment(self, user_id: str, original_name: str, raw_text: str, parsed: dict):
        from datetime import datetime, timezone
        self.db.table("profile_enrichments").upsert({
            "user_id": user_id,
            "resume_original_name": original_name,
            "resume_raw_text": raw_text,
            "resume_parsed": parsed,
            "resume_uploaded_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="user_id").execute()

    def get_enrichment(self, user_id: str) -> dict | None:
        result = self.db.table("profile_enrichments").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
