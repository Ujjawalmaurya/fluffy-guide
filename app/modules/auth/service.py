"""
Auth service — OTP generation/verification, token issuance.
Coordinates between security utils, repository, and logging.
"""
from datetime import datetime, timedelta, timezone

from app.core.security import generate_otp, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.logger import get_logger
from app.modules.auth.repository import AuthRepository
from app.schemas.enums import UserRole
from app.schemas.response.auth import TokenResponse
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

    def signup(self, email: str, role: UserRole):
        """Create user if not exists and send OTP."""
        user = self.repo.get_user_by_email(email)
        if user:
            from app.shared.exceptions import Conflict
            raise Conflict("User already exists. Please login instead.")
        
        self.repo.create_user(email, role)
        return self.request_otp(email)

    def login(self, email: str):
        """Check if user exists and send OTP."""
        user = self.repo.get_user_by_email(email)
        if not user:
            from app.shared.exceptions import UserNotFound
            raise UserNotFound("User not found. Please signup first.")
        
        return self.request_otp(email)

    def verify_otp(self, email: str, otp_code: str) -> dict:
        """Verify OTP, return JWT tokens + user data with role."""
        record = self.repo.get_latest_otp(email)

        if not record:
            raise OTPNotFound()

        if record["is_used"]:
            raise OTPAlreadyUsed()

        # Check expiry
        expires_at_str = record["expires_at"]
        if isinstance(expires_at_str, str):
            expires_at_str = expires_at_str.replace(" ", "T")
            expires_at = datetime.fromisoformat(expires_at_str)
        else:
            expires_at = expires_at_str

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        log.debug(f"Current time: {datetime.now(timezone.utc)}, Expires at: {expires_at}")
        if datetime.now(timezone.utc) > expires_at:
            log.warning(f"OTP Expired for {email}. Current time: {datetime.now(timezone.utc)}, Expires at: {expires_at}")
            raise OTPExpired()

        log.debug(f"Expected OTP: '{record['otp_code']}', Received OTP: '{otp_code}'")
        if str(record["otp_code"]).strip() != str(otp_code).strip():
            log.warning(f"OTP Invalid for {email}. Expected: '{record['otp_code']}', Received: '{otp_code}'")
            raise OTPInvalid()

        # All good — mark used and fetch user
        self.repo.mark_otp_used(record["id"])
        user = self.repo.get_or_create_user(email)

        log.info(f"OTP verified for {email}. User id={user['id']}, role={user.get('user_type')}, onboarding_done={user.get('onboarding_done')}")

        # Include role in JWT
        access_token = create_access_token(user["id"], role=user.get("user_type"))
        refresh_token = create_refresh_token(user["id"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    def refresh_tokens(self, user_id: str) -> TokenResponse:
        """Issue new token pair for valid refresh token."""
        user = self.repo.get_user_by_id(user_id)
        if not user:
            from app.shared.exceptions import Unauthorized
            raise Unauthorized()

        access_token = create_access_token(user_id, role=user.get("user_type"))
        refresh_token = create_refresh_token(user_id)
        log.info(f"Tokens refreshed for user={user_id}")
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
