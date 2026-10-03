"""Chat repository — all DB ops for chat_messages table."""
from supabase import Client
from app.core.logger import get_logger

log = get_logger("AI_CHAT")


class ChatRepository:
    def __init__(self, db: Client):
        self.db = db

    def add_message(self, user_id: str, role: str, content: str, language: str) -> dict:
        result = self.db.table("chat_messages").insert({
            "user_id": user_id,
            "role": role,
            "content": content,
            "language": language,
        }).execute()
        return result.data[0]

    def get_history(self, user_id: str, limit: int = 10) -> list[dict]:
        result = self.db.table("chat_messages") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        # Return in chronological order for context window
        return list(reversed(result.data or []))

    def clear_history(self, user_id: str):
        self.db.table("chat_messages").delete().eq("user_id", user_id).execute()
        log.info(f"Chat history cleared for user={user_id}")
