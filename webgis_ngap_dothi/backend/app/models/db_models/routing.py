"""
db_models/routing.py - SQLAlchemy ORM model cho mạng lưới đường giao thông
Dữ liệu được import từ OpenStreetMap qua osm2pgsql hoặc QGIS
"""

from sqlalchemy import Column, Integer, BigInteger, Float, String, Boolean, ForeignKey
from geoalchemy2 import Geometry

from app.repositories.db_connection import Base


class RoadNode(Base):
    """Nút giao thông (giao lộ, điểm đầu/cuối đoạn đường)"""
    __tablename__ = "road_nodes"

    id      = Column(BigInteger, primary_key=True, index=True)
    geom    = Column(Geometry("POINT", srid=4326), nullable=False)
    osm_id  = Column(BigInteger, nullable=True, index=True)

    def __repr__(self):
        return f"<RoadNode id={self.id}>"


class RoadEdge(Base):
    """Cạnh đường (đoạn đường nối 2 nút)"""
    __tablename__ = "road_edges"

    id          = Column(Integer, primary_key=True, index=True)
    source      = Column(BigInteger, ForeignKey("road_nodes.id"), nullable=False, index=True)
    target      = Column(BigInteger, ForeignKey("road_nodes.id"), nullable=False, index=True)
    geom        = Column(Geometry("LINESTRING", srid=4326), nullable=False)
    osm_id      = Column(BigInteger, nullable=True)

    # Thuộc tính đường
    name        = Column(String(200), nullable=True)
    road_type   = Column(String(50),  nullable=True)   # primary, secondary, residential...
    length_m    = Column(Float, nullable=False)         # Độ dài thực tế (mét)
    max_speed   = Column(Integer, default=50)           # km/h
    oneway      = Column(Boolean, default=False)

    # Thông tin ngập (cập nhật theo kịch bản)
    flood_depth_m  = Column(Float, default=0.0)        # Độ sâu ngập hiện tại
    is_blocked     = Column(Boolean, default=False)    # Bị chặn do ngập

    # Chi phí di chuyển (tính lại khi có ngập)
    cost_normal    = Column(Float, nullable=True)      # Chi phí bình thường
    cost_flooded   = Column(Float, nullable=True)      # Chi phí khi ngập

    def __repr__(self):
        return f"<RoadEdge id={self.id} {self.source}→{self.target} {self.length_m:.1f}m>"

