"""
repositories/routing_repo.py - SQL truy vấn mạng lưới đường giao thông
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from typing import List, Tuple, Optional

from app.models.db_models.routing import RoadNode, RoadEdge


class RoutingRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_edges(self, include_blocked: bool = False) -> List[RoadEdge]:
        """Lấy tất cả cạnh đường để xây dựng graph"""
        stmt = select(RoadEdge)
        if not include_blocked:
            stmt = stmt.where(RoadEdge.is_blocked == False)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_nearest_node(self, lng: float, lat: float) -> Optional[RoadNode]:
        """Tìm node gần nhất với tọa độ cho trước (dùng PostGIS ST_Distance)"""
        sql = text("""
            SELECT id, ST_X(geom) AS lng, ST_Y(geom) AS lat,
                   ST_Distance(
                       geom::geography,
                       ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
                   ) AS dist_m
            FROM road_nodes
            ORDER BY geom <-> ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
            LIMIT 1
        """)
        result = await self.db.execute(sql, {"lng": lng, "lat": lat})
        return result.fetchone()

    async def get_edges_in_flood_zone(self, scenario_mm: int) -> List[dict]:
        """
        Lấy các cạnh đường nằm trong vùng ngập theo kịch bản.
        Dùng PostGIS ST_Intersects để kiểm tra giao nhau.
        """
        sql = text("""
            SELECT e.id, e.source, e.target, e.length_m,
                   COALESCE(AVG(fp.depth_m), 0) AS flood_depth_m
            FROM road_edges e
            JOIN flood_zones fz ON ST_Intersects(e.geom, fz.geom)
            LEFT JOIN flood_points fp ON ST_DWithin(
                fp.geom::geography, e.geom::geography, 50
            )
            WHERE fz.scenario_mm = :scenario
            GROUP BY e.id, e.source, e.target, e.length_m
        """)
        result = await self.db.execute(sql, {"scenario": scenario_mm})
        return result.mappings().all()

    async def update_edge_flood_status(self, edge_id: int,
                                        flood_depth_m: float,
                                        is_blocked: bool) -> None:
        """Cập nhật trạng thái ngập của cạnh đường"""
        stmt = (
            update(RoadEdge)
            .where(RoadEdge.id == edge_id)
            .values(flood_depth_m=flood_depth_m, is_blocked=is_blocked)
        )
        await self.db.execute(stmt)

    async def reset_flood_status(self) -> None:
        """Reset toàn bộ trạng thái ngập về 0"""
        stmt = (
            update(RoadEdge)
            .values(flood_depth_m=0.0, is_blocked=False)
        )
        await self.db.execute(stmt)

    async def get_node_coordinates(self, node_id: int) -> Optional[Tuple[float, float]]:
        """Lấy tọa độ (lng, lat) của một node"""
        sql = text("""
            SELECT ST_X(geom) AS lng, ST_Y(geom) AS lat
            FROM road_nodes WHERE id = :node_id
        """)
        result = await self.db.execute(sql, {"node_id": node_id})
        row = result.fetchone()
        return (row.lng, row.lat) if row else None

