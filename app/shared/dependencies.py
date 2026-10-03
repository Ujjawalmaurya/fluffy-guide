"""
FastAPI dependencies — injected via Depends() in route handlers.
Keep business logic out of here — just extraction and validation.
"""
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_access_token
from app.core.database import get_supabase
from app.core.config import settings
from app.core.logger import get_logger

log = get_logger("DEPS")
bearer = HTTPBearer(auto_error=False)


def get_db():
    """Returns the Supabase client. Nothing fancy — just keeps imports clean."""
    return get_supabase()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    token: str = None,
    db=Depends(get_db),
) -> dict:
    """
    Verify Bearer token, return user dict from DB.
    Allows token to be passed via Authorization header OR 'token' query param (for SSE).
    Raises 401 on invalid/expired token or missing user.
    """
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error_code": "AUTH_TOKEN_MISSING", "message": "Missing authentication token.", "details": {}}
        )

    user_id = verify_access_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error_code": "AUTH_TOKEN_INVALID", "message": "Invalid or expired token.", "details": {}}
        )

    try:
        result = db.table("users").select("*").eq("id", user_id).maybe_single().execute()
        user_data = result.data
    except Exception:
        user_data = None

    if not user_data:
        # Check if user is a demo persona
        from app.modules.demo.personas import PERSONA_MAP
        for p in PERSONA_MAP.values():
            if p["id"] == user_id:
                return {
                    "id": p["id"],
                    "email": p["email"],
                    "user_type": p["type"],
                    "preferred_lang": "en",
                    "onboarding_done": True,
                    "full_name": p["name"],
                }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error_code": "AUTH_UNAUTHORIZED", "message": "User not found.", "details": {}}
        )

    return user_data


async def get_officer_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Restricts access to users with 'government_officer' or 'admin' user_type.
    """
    user_type = current_user.get("user_type", "individual_youth")
    if user_type not in ["government_officer", "admin"]:
        log.warning(f"Unauthorized government access attempt by user {current_user.get('id')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "error_code": "OFFICER_UNAUTHORIZED", "message": "Officer-only access required.", "details": {}}
        )
    return current_user


async def get_admin(x_admin_secret: str = Header(None)) -> bool:
    """
    Admin-only routes — check X-Admin-Secret header.
    No separate admin user table; just a shared secret.
    """
    if x_admin_secret != settings.admin_secret:
        log.warning("Admin access attempted with wrong secret")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "error_code": "ADMIN_UNAUTHORIZED", "message": "Invalid admin secret.", "details": {}}
        )
    return True
