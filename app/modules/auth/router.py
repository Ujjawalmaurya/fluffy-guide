"""
Auth router — HTTP endpoints only.
Parses request → calls service → returns response.
No business logic here.
"""
from fastapi import APIRouter, Depends
from app.modules.auth.service import AuthService
from app.modules.auth.repository import AuthRepository
from app.schemas.request.auth import (
    OTPRequest, SignupRequest, OTPVerifyRequest, TokenRefreshRequest
)
from app.schemas.response.auth import TokenResponse, UserAuthResponse
from app.shared.dependencies import get_db, get_current_user
from app.shared.response_models import ok, APIResponse
from app.core.security import verify_refresh_token
from app.shared.exceptions import TokenInvalid

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_service(db=Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(db))


@router.post("/signup", response_model=APIResponse)
async def signup(body: SignupRequest, service: AuthService = Depends(_get_service)):
    service.signup(body.email, body.role)
    return ok(message="Signup successful. OTP sent to your email.")


@router.post("/login", response_model=APIResponse)
async def login(body: OTPRequest, service: AuthService = Depends(_get_service)):
    service.login(body.email)
    return ok(message="Login initiated. OTP sent to your email.")


@router.post("/request-otp", response_model=APIResponse)
async def request_otp(body: OTPRequest, service: AuthService = Depends(_get_service)):
    """Legacy endpoint — redirects to login logic."""
    service.login(body.email)
    return ok(message="OTP generated (check server logs)")


@router.post("/verify-otp", response_model=APIResponse[TokenResponse])
async def verify_otp(body: OTPVerifyRequest, service: AuthService = Depends(_get_service)):
    result = service.verify_otp(body.email, body.otp)
    return ok(data=result)


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_tokens(body: TokenRefreshRequest, service: AuthService = Depends(_get_service)):
    user_id = verify_refresh_token(body.refresh_token)
    if not user_id:
        raise TokenInvalid()
    result = service.refresh_tokens(user_id)
    return ok(data=result)


@router.get("/me", response_model=APIResponse[UserAuthResponse])
async def get_me(current_user: dict = Depends(get_current_user)):
    return ok(data=current_user)
