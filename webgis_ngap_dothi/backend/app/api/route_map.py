"""
api/route_map.py - Controller lấy lớp bản đồ, điểm ngập, kịch bản
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.repositories.db_connection import get_db
from app.services.gis_service import GisService
from app.services.flood_analysis_service import FloodAnalysisService

router = APIRouter()


@router.get("/flood-layer")
async def get_flood_layer(
    scenario: Optional[int] = Query(None, description="Kịch bản mưa mm: 100, 200, 300"),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy lớp ngập GeoJSON.
    - Không có scenario → trả về tất cả điểm ngập đã xác minh
    - Có scenario (100/200/300mm) → trả về vùng ngập theo kịch bản
    """
    svc = GisService(db)
    return await svc.get_flood_layer(scenario_mm=scenario)


@router.get("/flood-points")
async def get_flood_points(
    scenario: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lấy tất cả điểm ngập dạng GeoJSON"""
    from app.repositories.flood_repo import FloodRepository
    repo = FloodRepository(db)
    return await repo.get_flood_points_geojson(scenario=scenario)


@router.get("/scenarios/{scenario_mm}")
async def run_scenario(
    scenario_mm: int,
    db: AsyncSession = Depends(get_db),
):
    """Chạy hoặc lấy kịch bản ngập theo mm mưa"""
    svc = FloodAnalysisService(db)
    return await svc.run_flood_scenario(scenario_mm)


@router.get("/statistics")
async def get_statistics(
    scenario: int = Query(100),
    db: AsyncSession = Depends(get_db),
):
    """Thống kê vùng ngập theo kịch bản"""
    svc = FloodAnalysisService(db)
    return await svc.get_flood_statistics(scenario)


@router.get("/dem-info")
async def get_dem_info(db: AsyncSession = Depends(get_db)):
    """Thông tin DEM (độ phân giải, bounds, CRS)"""
    svc = GisService(db)
    return await svc.get_dem_info()


@router.get("/elevation")
async def get_elevation(
    lng: float = Query(..., description="Kinh độ"),
    lat: float = Query(..., description="Vĩ độ"),
    db: AsyncSession = Depends(get_db),
):
    """Lấy độ cao tại một điểm GPS"""
    svc = GisService(db)
    return await svc.get_elevation_at_point(lng, lat)

