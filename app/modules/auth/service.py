"""
Auth service — OTP generation/verification, token issuance.
Coordinates between security utils, repository, and logging.
"""
from datetime import datetime, timedelta, timezone

from app.core.security import generate_otp, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.logger import get_logger
from app.modules.auth.repository import AuthRepository
from app.shared.exceptions import OTPNotFound, OTPExpired, OTPAlreadyUsed, OTPInvalid

log = get_logger("AUTH")


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def request_otp(self, email: str) -> str:
        """Generate OTP, store it, print to terminal. Returns the OTP (for logging only)."""
        otp = generate_otp()
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=settings.otp_expire_minutes)).isoformat()
        self.repo.create_otp(email, otp, expires_at)
        # Print directly — loguru can buffer but print won't
        print(f"\n{'='*40}\n OTP for {email} → {otp}\n{'='*40}\n", flush=True)
        log.info(f"OTP for {email} → {otp}")
        return otp

    def verify_otp(self, email: str, otp_code: str) -> dict:
        """Verify OTP, upsert user, return JWT tokens + user data."""
        record = self.repo.get_latest_otp(email)

        if not record:
            raise OTPNotFound()

        if record["is_used"]:
            raise OTPAlreadyUsed()

        # Check expiry
        expires_at = datetime.fromisoformat(record["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise OTPExpired()

        if record["otp_code"] != otp_code:
            raise OTPInvalid()

        # All good — mark used and create/fetch user
        self.repo.mark_otp_used(record["id"])
        user = self.repo.upsert_user(email)

        log.info(f"OTP verified for {email}. User id={user['id']}")

        access_token = create_access_token(user["id"])
        refresh_token = create_refresh_token(user["id"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    def refresh_tokens(self, user_id: str) -> dict:
        """Issue new token pair for valid refresh token."""
        user = self.repo.get_user_by_id(user_id)
        if not user:
            from app.shared.exceptions import Unauthorized
            raise Unauthorized()

        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        log.info(f"Tokens refreshed for user={user_id}")
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
