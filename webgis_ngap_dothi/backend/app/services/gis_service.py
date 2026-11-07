"""
services/gis_service.py - Điều phối tổng hợp các tác vụ GIS
Đóng vai trò facade cho raster_service và flood_analysis_service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.services.raster_service import RasterService
from app.services.flood_analysis_service import FloodAnalysisService
from app.repositories.flood_repo import FloodRepository


class GisService:

    def __init__(self, db: AsyncSession):
        self.db              = db
        self.raster_svc      = RasterService()
        self.flood_analysis  = FloodAnalysisService(db)
        self.flood_repo      = FloodRepository(db)

    async def get_flood_layer(self, scenario_mm: Optional[int] = None) -> dict:
        """
        Lấy lớp ngập GeoJSON.
        Nếu có scenario → trả về vùng ngập theo kịch bản.
        Nếu không → trả về tất cả điểm ngập đã xác minh.
        """
        if scenario_mm:
            # Thử lấy từ DB trước
            geojson = await self.flood_repo.get_flood_zones_geojson(scenario_mm)
            if not geojson.get("features"):
                # Chưa có → chạy phân tích mới
                geojson = await self.flood_analysis.run_flood_scenario(scenario_mm)
            return geojson
        else:
            return await self.flood_repo.get_flood_points_geojson()

    async def get_dem_info(self) -> dict:
        """Trả về metadata của DEM cho frontend hiển thị"""
        try:
            return self.raster_svc.get_dem_info()
        except (FileNotFoundError, RuntimeError) as e:
            return {"error": str(e), "available": False}

    async def get_elevation_at_point(self, lng: float, lat: float) -> dict:
        """Trả về độ cao tại một điểm GPS"""
        try:
            elevation = self.raster_svc.get_elevation_at_point(lng, lat)
            return {"longitude": lng, "latitude": lat, "elevation_m": elevation}
        except Exception as e:
            return {"longitude": lng, "latitude": lat, "elevation_m": None, "error": str(e)}

