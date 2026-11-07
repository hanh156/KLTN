"""
security.py - Xử lý bảo mật: hash password, tạo/xác minh JWT token
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ------------------------------------------------------------------ #
#  Password Hashing
# ------------------------------------------------------------------ #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Băm mật khẩu trước khi lưu vào DB"""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu nhập vào khớp với hash trong DB"""
    return pwd_context.verify(plain_password, hashed_password)


# ------------------------------------------------------------------ #
#  JWT Token
# ------------------------------------------------------------------ #
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT access token.
    data: thường chứa {"sub": user_id, "role": "user" | "admin"}
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Tạo refresh token có thời hạn dài hơn"""
    return create_access_token(
        data, expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str) -> Optional[dict]:
    """
    Giải mã JWT token.
    Trả về payload nếu hợp lệ, None nếu hết hạn hoặc sai.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

