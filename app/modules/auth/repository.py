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
        # 1. Try to find existing record
        existing = self.db.table("otp_store").select("*").eq("email", email).execute()
        
        if existing.data:
            # 2. Update existing
            result = self.db.table("otp_store").update({
                "otp_code": otp_code,
                "expires_at": expires_at,
                "is_used": False,
            }).eq("email", email).execute()
        else:
            # 3. Insert new
            result = self.db.table("otp_store").insert({
                "email": email,
                "otp_code": otp_code,
                "expires_at": expires_at,
                "is_used": False,
            }).execute()
            
        return result.data[0]

    def mark_otp_used(self, otp_id: str):
        self.db.table("otp_store").update({"is_used": True}).eq("id", otp_id).execute()

    def create_user(self, email: str, role: str) -> dict:
        """Create a new user with a specific role. Fails if user already exists."""
        result = self.db.table("users").insert({
            "email": email,
            "user_type": role,
            "onboarding_done": False
        }).execute()
        return result.data[0]

    def get_or_create_user(self, email: str) -> dict:
        """Fetch user by email. Note: Signup handles the creation with role."""
        result = self.db.table("users").select("*").eq("email", email).execute()
        if result.data:
            return result.data[0]
        
        # This shouldn't be reached in the new flow as signup is mandatory for new users
        # but kept for backward compatibility/robustness.
        result = self.db.table("users").upsert({"email": email}, on_conflict="email").execute()
        return result.data[0]

    def get_user_by_id(self, user_id: str) -> dict | None:
        result = self.db.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None

    def get_user_by_email(self, email: str) -> dict | None:
        result = self.db.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
