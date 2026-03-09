from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService, AuthService
from app.schemas.user import Token, UserOut, RoleSelection
from app.core.config import settings
from app.models.user import User
from app.api.deps import get_current_user
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google", response_model=Token)
async def auth_google(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        raise HTTPException(status_code=400, detail="OAuth error")
        
    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="No user info from Google")
        
    user_service = UserService(db)
    user = user_service.get_or_create_google_user(user_info)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email, "user_type": user.user_type}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/setup-role", response_model=UserOut)
def setup_role(
    setup_in: RoleSelection, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type is not None:
        raise HTTPException(status_code=400, detail="User type already configured")
    
    user_service = UserService(db)
    return user_service.complete_user_setup(current_user, setup_in)
