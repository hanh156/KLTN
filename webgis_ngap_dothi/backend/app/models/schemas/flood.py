"""
schemas/flood.py - Pydantic schemas cho FloodPoint và FloodZone
"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class FloodSeverity(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


# ---------- Request schemas ---------- #

class FloodPointCreate(BaseModel):
    longitude:  float
    latitude:   float
    depth_m:    float
    severity:   FloodSeverity
    scenario:   Optional[int] = None
    source:     str = "manual"


# ---------- Response schemas ---------- #

class FloodPointResponse(BaseModel):
    id:          int
    longitude:   float
    latitude:    float
    depth_m:     float
    severity:    FloodSeverity
    scenario:    Optional[int]
    source:      str
    recorded_at: datetime

    model_config = {"from_attributes": True}


class FloodZoneResponse(BaseModel):
    id:          int
    scenario_mm: int
    avg_depth_m: Optional[float]
    area_sqm:    Optional[float]
    geojson:     Any  # GeoJSON geometry object
    created_at:  datetime

    model_config = {"from_attributes": True}


class FloodLayerResponse(BaseModel):
    """Trả về toàn bộ lớp ngập dạng GeoJSON FeatureCollection"""
    type:     str = "FeatureCollection"
    features: List[Any]
    scenario_mm: Optional[int] = None

