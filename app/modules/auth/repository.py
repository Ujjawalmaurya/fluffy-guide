"""
Auth repository — all database queries for auth operations.
No business logic here, just DB in/out.
"""
from datetime import datetime, timezone
from supabase import Client
from app.core.logger import get_logger

log = get_logger("AUTH")


class AuthRepository:
    def __init__(self, db: Client):
        self.db = db

    def get_latest_otp(self, email: str) -> dict | None:
        result = self.db.table("otp_store") \
            .select("*") \
            .eq("email", email) \
            .eq("is_used", False) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None

    def create_otp(self, email: str, otp_code: str, expires_at: str) -> dict:
        result = self.db.table("otp_store").insert({
            "email": email,
            "otp_code": otp_code,
            "expires_at": expires_at,
        }).execute()
        return result.data[0]

    def mark_otp_used(self, otp_id: str):
        self.db.table("otp_store").update({"is_used": True}).eq("id", otp_id).execute()

    def upsert_user(self, email: str) -> dict:
        # Insert if not exists, return existing if already there
        result = self.db.table("users").upsert({"email": email}, on_conflict="email").execute()
        return result.data[0]

    def get_user_by_id(self, user_id: str) -> dict | None:
        result = self.db.table("users").select("*").eq("id", user_id).single().execute()
        return result.data

    def get_user_by_email(self, email: str) -> dict | None:
        result = self.db.table("users").select("*").eq("email", email).single().execute()
        return result.data
