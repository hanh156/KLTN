"""
services/flood_analysis_service.py - Phân tích và mô phỏng vùng ngập từ DEM
"""

import numpy as np
import json
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.raster_service import RasterService
from app.repositories.flood_repo import FloodRepository
from app.core.config import settings


class FloodAnalysisService:

    # Mực nước tương ứng với từng kịch bản mưa (mét, tương đối)
    SCENARIO_WATER_LEVEL: Dict[int, float] = {
        100: 0.3,   # Mưa 100mm → mực nước +0.3m
        200: 0.5,   # Mưa 200mm → mực nước +0.5m
        300: 0.8,   # Mưa 300mm → mực nước +0.8m
    }

    def __init__(self, db: AsyncSession):
        self.raster_svc = RasterService()
        self.flood_repo = FloodRepository(db)

    async def run_flood_scenario(self, scenario_mm: int) -> dict:
        """
        Chạy kịch bản ngập theo lượng mưa (mm).
        1. Tính water_level từ scenario
        2. Tạo flood mask từ DEM
        3. Chuyển mask → polygon GeoJSON
        4. Lưu vào DB flood_zones
        5. Trả về GeoJSON FeatureCollection
        """
        water_level = self.SCENARIO_WATER_LEVEL.get(scenario_mm, 0.3)

        try:
            flood_mask, transform, crs = self.raster_svc.compute_flood_mask(water_level)
            geojson = self._mask_to_geojson(flood_mask, transform)
            area_sqm = float(np.sum(flood_mask)) * abs(transform.a * transform.e)

            # Lưu vào DB
            await self.flood_repo.upsert_flood_zone(
                scenario_mm=scenario_mm,
                geojson_geom=f"MULTIPOLYGON EMPTY",  # Thay bằng WKT thực tế
                avg_depth_m=water_level,
                area_sqm=area_sqm,
            )
        except (FileNotFoundError, RuntimeError):
            # Nếu không có DEM → lấy từ DB (dữ liệu đã xử lý trước)
            geojson = await self.flood_repo.get_flood_zones_geojson(scenario_mm)

        return geojson

    def _mask_to_geojson(self, flood_mask: np.ndarray, transform) -> dict:
        """
        Chuyển boolean numpy array → GeoJSON FeatureCollection (polygons).
        Dùng rasterio.features.shapes để vectorize.
        """
        try:
            from rasterio.features import shapes
            from shapely.geometry import shape, mapping
            from shapely.ops import unary_union

            mask_uint8 = flood_mask.astype(np.uint8)
            polygons = []
            for geom_dict, val in shapes(mask_uint8, transform=transform):
                if val == 1:  # Chỉ lấy vùng ngập
                    polygons.append(shape(geom_dict))

            if not polygons:
                return {"type": "FeatureCollection", "features": []}

            merged = unary_union(polygons)
            return {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": mapping(merged),
                    "properties": {},
                }]
            }
        except ImportError:
            return {"type": "FeatureCollection", "features": []}

    async def get_flood_statistics(self, scenario_mm: int) -> dict:
        """Thống kê vùng ngập theo kịch bản"""
        geojson = await self.flood_repo.get_flood_zones_geojson(scenario_mm)
        points  = await self.flood_repo.get_all_flood_points(scenario=scenario_mm)

        return {
            "scenario_mm":    scenario_mm,
            "total_zones":    len(geojson.get("features", [])),
            "total_points":   len(points),
            "severity_count": {
                "low":    sum(1 for p in points if p.severity == "low"),
                "medium": sum(1 for p in points if p.severity == "medium"),
                "high":   sum(1 for p in points if p.severity == "high"),
            }
        }

