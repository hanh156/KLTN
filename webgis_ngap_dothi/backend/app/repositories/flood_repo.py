"""
repositories/flood_repo.py - SQL tương tác bảng flood_points, flood_zones
Nơi DUY NHẤT chứa câu lệnh SQL liên quan đến ngập
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, text
from typing import List, Optional
from geoalchemy2.functions import ST_AsGeoJSON, ST_SetSRID, ST_MakePoint

from app.models.db_models.flood import FloodPoint, FloodZone


class FloodRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------- FloodPoint -------------------- #

    async def get_all_flood_points(self, scenario: Optional[int] = None) -> List[FloodPoint]:
        """Lấy tất cả điểm ngập, lọc theo kịch bản nếu có"""
        stmt = select(FloodPoint)
        if scenario:
            stmt = stmt.where(FloodPoint.scenario == scenario)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_flood_points_geojson(self, scenario: Optional[int] = None) -> dict:
        """Trả về điểm ngập dạng GeoJSON FeatureCollection"""
        where_clause = f"AND scenario = {scenario}" if scenario else ""
        sql = text(f"""
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', COALESCE(json_agg(
                    json_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(geom)::json,
                        'properties', json_build_object(
                            'id', id,
                            'depth_m', depth_m,
                            'severity', severity,
                            'scenario', scenario,
                            'source', source,
                            'recorded_at', recorded_at
                        )
                    )
                ), '[]'::json)
            ) AS geojson
            FROM flood_points
            WHERE 1=1 {where_clause}
        """)
        result = await self.db.execute(sql)
        row = result.fetchone()
        return row.geojson if row else {"type": "FeatureCollection", "features": []}

    async def create_flood_point(self, lng: float, lat: float, depth_m: float,
                                  severity: str, scenario: int = None,
                                  source: str = "manual") -> FloodPoint:
        """Thêm điểm ngập mới"""
        point = FloodPoint(
            geom=f"SRID=4326;POINT({lng} {lat})",
            depth_m=depth_m,
            severity=severity,
            scenario=scenario,
            source=source,
        )
        self.db.add(point)
        await self.db.flush()
        return point

    # -------------------- FloodZone -------------------- #

    async def get_flood_zones_geojson(self, scenario_mm: int) -> dict:
        """Trả về vùng ngập theo kịch bản dạng GeoJSON"""
        sql = text("""
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'scenario_mm', :scenario,
                'features', COALESCE(json_agg(
                    json_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(geom)::json,
                        'properties', json_build_object(
                            'id', id,
                            'scenario_mm', scenario_mm,
                            'avg_depth_m', avg_depth_m,
                            'area_sqm', area_sqm
                        )
                    )
                ), '[]'::json)
            ) AS geojson
            FROM flood_zones
            WHERE scenario_mm = :scenario
        """)
        result = await self.db.execute(sql, {"scenario": scenario_mm})
        row = result.fetchone()
        return row.geojson if row else {"type": "FeatureCollection", "features": []}

    async def upsert_flood_zone(self, scenario_mm: int, geojson_geom: str,
                                 avg_depth_m: float = None, area_sqm: float = None) -> FloodZone:
        """Tạo hoặc cập nhật vùng ngập theo kịch bản"""
        # Xóa vùng ngập cũ cùng kịch bản
        old = await self.db.execute(
            select(FloodZone).where(FloodZone.scenario_mm == scenario_mm)
        )
        for zone in old.scalars().all():
            await self.db.delete(zone)

        zone = FloodZone(
            geom=f"SRID=4326;{geojson_geom}",
            scenario_mm=scenario_mm,
            avg_depth_m=avg_depth_m,
            area_sqm=area_sqm,
        )
        self.db.add(zone)
        await self.db.flush()
        return zone

