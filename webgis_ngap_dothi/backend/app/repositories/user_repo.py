"""
repositories/user_repo.py - SQL truy vấn tài khoản người dùng
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List

from app.models.db_models.user import User, UserRole


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, limit: int = 20) -> List[User]:
        result = await self.db.execute(
            select(User)
            .offset((page - 1) * limit)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, username: str, email: str, hashed_password: str,
                     full_name: str = None, role: UserRole = UserRole.USER) -> User:
        """Tạo tài khoản mới"""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Cập nhật thông tin user"""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**kwargs)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate(self, user_id: int) -> None:
        """Vô hiệu hóa tài khoản (soft delete)"""
        await self.update(user_id, is_active=False)

    async def username_exists(self, username: str) -> bool:
        result = await self.db.execute(
            select(User.id).where(User.username == username)
        )
        return result.first() is not None

    async def email_exists(self, email: str) -> bool:
        result = await self.db.execute(
            select(User.id).where(User.email == email)
        )
        return result.first() is not None

