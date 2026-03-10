"""
Auth router — HTTP endpoints only.
Parses request → calls service → returns response.
No business logic here.
"""
from fastapi import APIRouter, Depends

from app.modules.auth.schemas import OTPRequest, OTPVerify, RefreshRequest
from app.modules.auth.service import AuthService
from app.modules.auth.repository import AuthRepository
from app.shared.dependencies import get_db, get_current_user
from app.shared.response_models import ok
from app.core.security import verify_refresh_token
from app.shared.exceptions import TokenInvalid

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_service(db=Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(db))


@router.post("/request-otp")
async def request_otp(body: OTPRequest, service: AuthService = Depends(_get_service)):
    service.request_otp(body.email)
    return ok(message="OTP generated (check server logs)")


@router.post("/verify-otp")
async def verify_otp(body: OTPVerify, service: AuthService = Depends(_get_service)):
    result = service.verify_otp(body.email, body.otp)
    return ok(data=result)


@router.post("/refresh")
async def refresh_tokens(body: RefreshRequest, service: AuthService = Depends(_get_service)):
    user_id = verify_refresh_token(body.refresh_token)
    if not user_id:
        raise TokenInvalid()
    result = service.refresh_tokens(user_id)
    return ok(data=result)


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return ok(data=current_user)
