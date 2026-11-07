"""
db_models/flood.py - SQLAlchemy ORM model cho bảng flood_points và flood_zones
Yêu cầu PostGIS extension trên PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import enum

from app.repositories.db_connection import Base


class FloodSeverity(str, enum.Enum):
    LOW    = "low"      # < 0.3m
    MEDIUM = "medium"   # 0.3 - 0.5m
    HIGH   = "high"     # > 0.5m


class FloodPoint(Base):
    """Điểm ngập đơn lẻ — từ cảm biến hoặc báo cáo đã xác minh"""
    __tablename__ = "flood_points"

    id          = Column(Integer, primary_key=True, index=True)
    geom        = Column(Geometry("POINT", srid=4326), nullable=False)  # PostGIS
    depth_m     = Column(Float, nullable=False, comment="Độ sâu ngập (mét)")
    severity    = Column(Enum(FloodSeverity), nullable=False)
    scenario    = Column(Integer, nullable=True, comment="Kịch bản mưa mm")
    source      = Column(String(50), default="manual")  # manual | sensor | report
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class FloodZone(Base):
    """Vùng ngập — polygon từ phân tích DEM/kịch bản"""
    __tablename__ = "flood_zones"

    id          = Column(Integer, primary_key=True, index=True)
    geom        = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
    scenario_mm = Column(Integer, nullable=False, comment="Lượng mưa mm")
    avg_depth_m = Column(Float, nullable=True)
    area_sqm    = Column(Float, nullable=True, comment="Diện tích vùng ngập (m²)")
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

