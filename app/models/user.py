from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
import enum
from pydantic import BaseModel, EmailStr

Base = declarative_base()

# User roles
class UserRole(enum.Enum):
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

# Database model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.ADMIN, nullable=False)

# Pydantic schemas for validation
class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserCreate(BaseModel):
    email: EmailStr

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for admin login request."""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
