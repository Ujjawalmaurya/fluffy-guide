from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User, EndUserProfile, OrgProfile, UserType
from app.repositories.user_repository import UserRepository, EndUserRepo, OrgRepo
from app.schemas.user import UserCreate, EndUserCreate, OrgCreate, RoleSelection
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.end_user_repo = EndUserRepo(db)
        self.org_repo = OrgRepo(db)

    def register_end_user(self, user_in: EndUserCreate):
        logger.info(f"Registering end user: {user_in.email}")
        hashed_pw = AuthService.get_password_hash(user_in.password)
        
        # SOLID: User and Profile are separated
        user = User(email=user_in.email, hashed_password=hashed_pw, user_type=UserType.END_USER)
        db_user = self.user_repo.create(user)
        
        profile = EndUserProfile(user_id=db_user.id, full_name=user_in.full_name, career_goals=user_in.career_goals)
        self.end_user_repo.create(profile)
        
        return db_user

    def register_org(self, user_in: OrgCreate):
        logger.info(f"Registering organization: {user_in.email}")
        hashed_pw = AuthService.get_password_hash(user_in.password)
        
        user = User(email=user_in.email, hashed_password=hashed_pw, user_type=UserType.ORGANIZATION)
        db_user = self.user_repo.create(user)
        
        profile = OrgProfile(user_id=db_user.id, org_name=user_in.org_name, org_type=user_in.org_type)
        self.org_repo.create(profile)
        
        return db_user

    def authenticate_user(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            return False
        if not AuthService.verify_password(password, user.hashed_password):
            return False
        return user

    def get_or_create_google_user(self, google_profile: dict):
        email = google_profile.get("email")
        user = self.user_repo.get_by_email(email)
        
        if not user:
            logger.info(f"Creating new Google user (pending role): {email}")
            user = User(
                email=email, 
                hashed_password=None,
                user_type=None # Must be set via /auth/setup-type
            )
            user = self.user_repo.create(user)
            
        return user

    def complete_user_setup(self, user: User, setup_in: RoleSelection):
        logger.info(f"Setting role for user {user.email}: {setup_in.user_type}")
        
        # Update user type
        user.user_type = setup_in.user_type
        self.db.add(user)
        
        # Create corresponding profile
        if setup_in.user_type == UserType.END_USER:
            profile = EndUserProfile(
                user_id=user.id, 
                full_name=setup_in.full_name or "New User",
                career_goals=setup_in.career_goals
            )
            self.end_user_repo.create(profile)
        elif setup_in.user_type == UserType.ORGANIZATION:
            profile = OrgProfile(
                user_id=user.id, 
                org_name=setup_in.org_name or "New Org",
                org_type=setup_in.org_type
            )
            self.org_repo.create(profile)
            
        self.db.commit()
        return user
