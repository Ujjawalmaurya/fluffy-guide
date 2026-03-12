from uuid import UUID
from datetime import datetime, timezone
from supabase import Client

class SkillProfileRepository:
    def __init__(self, db: Client):
        self.db = db
        
    def get_by_user_id(self, user_id: str | UUID) -> dict | None:
        res = self.db.table("user_skill_profiles").select("*").eq("user_id", str(user_id)).execute()
        return res.data[0] if res.data else None
        
    def upsert(self, user_id: str | UUID, skills: list[dict], resume_contributed: bool, assessment_contributed: bool) -> dict:
        # Get existing to preserve `profile_version` or we can just upsert.
        # Ensure we send the correct format
        data = {
            "user_id": str(user_id),
            "skills": skills,
            "resume_contributed": resume_contributed,
            "assessment_contributed": assessment_contributed,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        res = self.db.table("user_skill_profiles").upsert(data, on_conflict="user_id").execute()
        return res.data[0] if res.data else {}
        
    def increment_version(self, user_id: str | UUID) -> int:
        profile = self.get_by_user_id(user_id)
        current_version = profile.get("profile_version", 1) if profile else 1
        new_version = current_version + 1
        
        self.db.table("user_skill_profiles").update({
            "profile_version": new_version,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("user_id", str(user_id)).execute()
        
        return new_version
