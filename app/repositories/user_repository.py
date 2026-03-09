from sqlalchemy.orm import Session
from app.models.user import User, EndUserProfile, OrgProfile, UserType
from .base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

class EndUserRepo(BaseRepository[EndUserProfile]):
    def __init__(self, db: Session):
        super().__init__(EndUserProfile, db)

class OrgRepo(BaseRepository[OrgProfile]):
    def __init__(self, db: Session):
        super().__init__(OrgProfile, db)
