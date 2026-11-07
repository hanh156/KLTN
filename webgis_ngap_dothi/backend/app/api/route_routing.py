"""
api/route_routing.py - Controller tìm đường tránh ngập
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db_connection import get_db
from app.services.dijkstra_service import DijkstraService
from app.models.schemas.routing import RoutingRequest, RoutingResponse

router = APIRouter()


@router.post("/find-path", response_model=RoutingResponse)
async def find_path(
    request: RoutingRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Tìm đường tránh ngập từ điểm A đến điểm B.

    Body JSON:
    {
        "start": {"longitude": 106.7, "latitude": 10.8},
        "end":   {"longitude": 106.8, "latitude": 10.9},
        "avoid_flood": true,
        "scenario_mm": 100,
        "max_depth_m": 0.3
    }
    """
    svc = DijkstraService(db)
    return await svc.find_path(request)


@router.get("/graph-info")
async def get_graph_info(db: AsyncSession = Depends(get_db)):
    """Thông tin đồ thị giao thông (số node, edge)"""
    from app.repositories.routing_repo import RoutingRepository
    from sqlalchemy import text
    repo = RoutingRepository(db)
    result = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM road_nodes) AS total_nodes,
            (SELECT COUNT(*) FROM road_edges) AS total_edges,
            (SELECT COUNT(*) FROM road_edges WHERE is_blocked = true) AS blocked_edges
    """))
    row = result.fetchone()
    return {
        "total_nodes":   row.total_nodes,
        "total_edges":   row.total_edges,
        "blocked_edges": row.blocked_edges,
    }

