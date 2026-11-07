"""
schemas/routing.py - Pydantic schemas cho tìm đường tránh ngập
"""

from pydantic import BaseModel, field_validator
from typing import List, Optional, Tuple


class Coordinate(BaseModel):
    longitude: float
    latitude:  float


class RoutingRequest(BaseModel):
    """Request tìm đường từ điểm đầu đến điểm cuối"""
    start: Coordinate
    end:   Coordinate
    avoid_flood:    bool = True          # Có né vùng ngập không
    scenario_mm:    Optional[int] = 100  # Kịch bản mưa
    max_depth_m:    float = 0.3          # Ngưỡng ngập tối đa cho phép đi qua

    @field_validator("max_depth_m")
    @classmethod
    def depth_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Ngưỡng độ sâu phải >= 0")
        return v


class RouteSegment(BaseModel):
    """Một đoạn đường trong tuyến"""
    coordinates: List[Tuple[float, float]]  # [[lng, lat], ...]
    distance_m:  float
    is_flooded:  bool = False
    flood_depth: Optional[float] = None


class RoutingResponse(BaseModel):
    """Kết quả tuyến đường"""
    found:          bool
    total_distance_m: float
    total_time_min:   float
    segments:       List[RouteSegment]
    geojson:        dict          # GeoJSON LineString toàn tuyến
    flood_avoided:  bool
    warnings:       List[str] = []

