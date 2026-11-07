"""
db_connection.py - Kết nối PostgreSQL/PostGIS bằng SQLAlchemy async
Nơi duy nhất tạo engine và session factory
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ------------------------------------------------------------------ #
#  Engine async
# ------------------------------------------------------------------ #
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,       # In SQL ra console khi DEBUG=True
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,        # Kiểm tra kết nối trước mỗi lần dùng
)

# ------------------------------------------------------------------ #
#  Session Factory
# ------------------------------------------------------------------ #
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ------------------------------------------------------------------ #
#  Base class cho tất cả ORM models
# ------------------------------------------------------------------ #
class Base(DeclarativeBase):
    pass


# ------------------------------------------------------------------ #
#  Dependency Injection cho FastAPI
# ------------------------------------------------------------------ #
async def get_db() -> AsyncSession:
    """
    FastAPI dependency — inject vào mọi route cần DB.
    Dùng: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

