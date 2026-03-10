"""
Security utilities — OTP generation, JWT create/verify.
No password hashing needed since we use OTP-only auth.
"""
import random
import string
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings
from app.core.logger import get_logger

log = get_logger("SECURITY")


def generate_otp() -> str:
    """6-digit numeric OTP as string (zero-padded)."""
    return "".join(random.choices(string.digits, k=settings.otp_length))


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_expire_minutes)
    payload = {"sub": user_id, "type": "access", "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
    payload = {"sub": user_id, "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """Returns payload dict or None if invalid/expired."""
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        log.warning(f"Token decode failed: {e}")
        return None


def verify_access_token(token: str) -> str | None:
    """Returns user_id (sub) from a valid access token, else None."""
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload.get("sub")
    return None


def verify_refresh_token(token: str) -> str | None:
    """Returns user_id from a valid refresh token, else None."""
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload.get("sub")
    return None
