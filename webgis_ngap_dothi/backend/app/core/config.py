"""
config.py - Đọc biến môi trường tập trung từ file .env
Mọi nơi trong ứng dụng chỉ import settings từ đây
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # --- Ứng dụng ---
    APP_NAME: str = "WebGIS Ngập Đô Thị"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # --- Database PostgreSQL + PostGIS ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "webgis_ngap"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Dùng cho Alembic migrations (không async)"""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- JWT Authentication ---
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:5500"]

    # --- Đường dẫn dữ liệu GIS ---
    DATA_RAW_DIR: str = "data/raw"
    DATA_PROCESSED_DIR: str = "data/processed"
    DEM_FILE: str = "data/raw/dem.tif"

    # --- Kịch bản ngập (mm mưa) ---
    FLOOD_THRESHOLDS: List[int] = [100, 200, 300]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton — import settings ở mọi nơi
settings = Settings()

