"""
db_models/report.py - SQLAlchemy ORM model cho bảng flood_reports
Lưu báo cáo ngập do người dùng gửi lên
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import enum

from app.repositories.db_connection import Base


class ReportStatus(str, enum.Enum):
    PENDING  = "pending"   # Chờ duyệt
    VERIFIED = "verified"  # Đã xác minh
    REJECTED = "rejected"  # Từ chối


class FloodReport(Base):
    __tablename__ = "flood_reports"

    id          = Column(Integer, primary_key=True, index=True)
    geom        = Column(Geometry("POINT", srid=4326), nullable=False)
    description = Column(Text, nullable=True, comment="Mô tả tình trạng ngập")
    image_url   = Column(String(500), nullable=True, comment="Ảnh chụp điểm ngập")
    status      = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    
    # Người báo cáo
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter    = relationship("User", foreign_keys=[reporter_id])

    # Admin duyệt
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewer    = relationship("User", foreign_keys=[reviewed_by])
    review_note = Column(Text, nullable=True)

    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<FloodReport id={self.id} status={self.status}>"

