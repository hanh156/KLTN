"""
schemas/user.py - Pydantic schemas cho User (request/response)
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER  = "user"
    ADMIN = "admin"


# ---------- Request schemas ---------- #

class UserRegisterRequest(BaseModel):
    username:  str
    email:     EmailStr
    password:  str
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Mật khẩu phải ít nhất 6 ký tự")
        return v


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserUpdateRequest(BaseModel):
    full_name:  Optional[str] = None
    email:      Optional[EmailStr] = None
    is_active:  Optional[bool] = None


# ---------- Response schemas ---------- #

class UserResponse(BaseModel):
    id:         int
    username:   str
    email:      str
    full_name:  Optional[str]
    role:       UserRole
    is_active:  bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    user:          UserResponse

