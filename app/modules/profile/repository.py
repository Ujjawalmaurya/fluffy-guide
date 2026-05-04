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

    def upsert_enrichment(self, user_id: str, original_name: str, raw_text: str, parsed: dict, model: str = None):
        from datetime import datetime, timezone
        data = {
            "user_id": user_id,
            "resume_original_name": original_name,
            "resume_raw_text": raw_text,
            "gemini_extracted": parsed,
            "resume_parsed": parsed,    # Backward compatibility
            "resume_uploaded_at": datetime.now(timezone.utc).isoformat(),
            "extraction_status": "done",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if model:
            data["extraction_model"] = model
            
        self.db.table("profile_enrichments").upsert(data, on_conflict="user_id").execute()

    def update_enrichment_status(self, user_id: str, status: str, error: str = None):
        """Updates the status of resume extraction."""
        from datetime import datetime, timezone
        data = {
            "user_id": user_id,
            "extraction_status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        # If record doesn't exist, this will create a minimal one
        self.db.table("profile_enrichments").upsert(data, on_conflict="user_id").execute()

    def get_enrichment(self, user_id: str) -> dict | None:
        result = self.db.table("profile_enrichments").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    def log_activity(self, user_id: str, activity_type: str, description: str, metadata: dict = None):
        """Logs a user activity to the database."""
        try:
            self.db.table("user_activities").insert({
                "user_id": user_id,
                "activity_type": activity_type,
                "description": description,
                "metadata": metadata or {}
            }).execute()
        except Exception as e:
            log.error(f"Failed to log activity {activity_type} for user={user_id}: {e}")
