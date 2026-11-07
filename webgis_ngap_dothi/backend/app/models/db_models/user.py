"""
db_models/user.py - SQLAlchemy ORM model cho bảng users
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum

from app.repositories.db_connection import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50),  unique=True, nullable=False, index=True)
    email         = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name     = Column(String(100), nullable=True)
    role          = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active     = Column(Boolean, default=True, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role}>"

