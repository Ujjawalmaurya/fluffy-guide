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

    result = db.table("users").select("*").eq("id", user_id).single().execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error_code": "AUTH_UNAUTHORIZED", "message": "User not found.", "details": {}}
        )

    return result.data


def require_user_type(allowed_types: list[str]):
    """
    Dependency factory to restrict routes by user type.
    Example: Depends(require_user_type(["org_ngo"]))
    """
    async def dependency(current_user: dict = Depends(get_current_user)):
        if current_user.get("user_type") not in allowed_types:
            log.warning(f"Access denied for user {current_user['id']} (type: {current_user.get('user_type')}). Required: {allowed_types}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "error_code": "FORBIDDEN",
                    "message": f"Access denied. This endpoint is restricted to {allowed_types}.",
                    "details": {}
                }
            )
        return current_user
    return dependency


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


from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.modules.ai_chat.providers.base import ICompletionProvider, IStructuredProvider


def get_completion_provider() -> ICompletionProvider:
    """Returns the completion (reasoning) LLM provider instance."""
    return get_ollama_instance()


def get_structured_provider() -> IStructuredProvider:
    """Returns the structured (extraction) LLM provider instance."""
    return get_ollama_instance()

