"""
services/auth_service.py - Xử lý xác thực và phân quyền
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, hash_password, decode_token, create_access_token, create_refresh_token
from app.repositories.db_connection import get_db
from app.repositories.user_repo import UserRepository
from app.models.db_models.user import User, UserRole
from app.models.schemas.user import UserRegisterRequest, TokenResponse, UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class AuthService:

    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register(self, data: UserRegisterRequest) -> User:
        """Đăng ký tài khoản mới"""
        if await self.user_repo.username_exists(data.username):
            raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
        if await self.user_repo.email_exists(data.email):
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")

        return await self.user_repo.create(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )

    async def login(self, username: str, password: str) -> TokenResponse:
        """Đăng nhập, trả về JWT token"""
        user = await self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tên đăng nhập hoặc mật khẩu không đúng",
            )
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa")

        token_data = {"sub": str(user.id), "role": user.role.value}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
            user=UserResponse.model_validate(user),
        )


# ------------------------------------------------------------------ #
#  FastAPI Dependencies — dùng trong route để lấy user hiện tại
# ------------------------------------------------------------------ #

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")

    user = await UserRepository(db).get_by_id(int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Chỉ cho phép Admin truy cập"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền thực hiện")
    return current_user

