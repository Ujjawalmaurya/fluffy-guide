from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class UserType(str, enum.Enum):
    END_USER = "end_user"
    ORGANIZATION = "organization"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Null for OAuth users
    user_type = Column(Enum(UserType), nullable=True) # Selected after first login

    # Relationship to specific profiles
    end_user_profile = relationship("EndUserProfile", back_populates="user", uselist=False)
    org_profile = relationship("OrgProfile", back_populates="user", uselist=False)

class EndUserProfile(Base):
    __tablename__ = "end_user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String)
    career_goals = Column(String) # Simple for now
    
    user = relationship("User", back_populates="end_user_profile")

class OrgProfile(Base):
    __tablename__ = "org_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    org_name = Column(String, nullable=False)
    org_type = Column(String) # NGO, Training, Employer
    
    user = relationship("User", back_populates="org_profile")

# Admin usually doesn't need a profile in this simple system, 
# just the user_type="admin" flag is enough for dashboard access.
