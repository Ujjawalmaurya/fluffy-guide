"""Chat repository — all DB ops for chat_messages table."""
from supabase import Client
from app.core.logger import get_logger

log = get_logger("AI_CHAT")


class ChatRepository:
    def __init__(self, db: Client):
        self.db = db

    async def add_message(self, user_id: str, role: str, content: str, language: str) -> dict:
        result = self.db.table("chat_messages").insert({
            "user_id": user_id,
            "role": role,
            "content": content,
            "language": language,
        }).execute()
        return result.data[0]

    async def get_history(self, user_id: str, limit: int = 10) -> list[dict]:
        result = self.db.table("chat_messages") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        # Return in chronological order for context window
        return list(reversed(result.data or []))

    async def clear_history(self, user_id: str):
        self.db.table("chat_messages").delete().eq("user_id", user_id).execute()
        log.info(f"Chat history cleared for user={user_id}")

    async def get_full_user_data(self, user_id: str) -> dict:
        """Fetch all data needed for LLM context in parallel if possible (here sequential for simplicity with Supabase-py)."""
        user_res = self.db.table("users").select("*").eq("id", user_id).execute()
        profile_res = self.db.table("user_profiles").select("*").eq("user_id", user_id).execute()
        prefs_res = self.db.table("user_preferences").select("*").eq("user_id", user_id).execute()
        skills_res = self.db.table("user_skill_profiles").select("*").eq("user_id", user_id).execute()
        gaps_res = self.db.table("gap_analysis_reports").select("*").eq("user_id", user_id).execute()

        return {
            "user": user_res.data[0] if user_res.data else {},
            "profile": profile_res.data[0] if profile_res.data else {},
            "preferences": prefs_res.data[0] if prefs_res.data else {},
            "skills": skills_res.data[0] if skills_res.data else {},
            "gaps": gaps_res.data[0] if gaps_res.data else {},
        }
