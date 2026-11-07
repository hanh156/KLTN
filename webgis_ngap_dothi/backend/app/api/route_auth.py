"""
api/route_auth.py - Controller xử lý đăng ký / đăng nhập / đăng xuất
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db_connection import get_db
from app.services.auth_service import AuthService, get_current_user
from app.models.schemas.user import (
    UserRegisterRequest, TokenResponse, UserResponse
)
from app.models.db_models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Đăng ký tài khoản người dùng mới"""
    svc  = AuthService(db)
    user = await svc.register(data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db:   AsyncSession = Depends(get_db),
):
    """Đăng nhập — trả về access_token và refresh_token"""
    svc = AuthService(db)
    return await svc.login(form.username, form.password)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin người dùng hiện tại"""
    return UserResponse.model_validate(current_user)

