from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserType
from app.schemas.user import TokenData
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, user_type=user_type)
    except JWTError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
