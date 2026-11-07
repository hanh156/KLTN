"""
services/dijkstra_service.py - Xây graph NetworkX và tìm đường Dijkstra/A*
Đây là phần thuật toán cốt lõi của dự án
"""

import math
import networkx as nx
from typing import List, Optional, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.routing_repo import RoutingRepository
from app.models.schemas.routing import RoutingRequest, RoutingResponse, RouteSegment


# ------------------------------------------------------------------ #
#  Hàm tính chi phí cạnh có xét ngập
# ------------------------------------------------------------------ #
FLOOD_BLOCK_DEPTH = 0.5    # m — ngập sâu hơn này thì chặn hoàn toàn
FLOOD_PENALTY_FACTOR = 10  # Nhân chi phí khi đường bị ngập nhẹ

def compute_edge_cost(length_m: float, flood_depth_m: float,
                       max_depth_allowed: float = 0.3) -> float:
    """
    Tính chi phí di chuyển qua một cạnh đường.

    - Không ngập             : cost = length_m
    - Ngập < max_depth_allowed: cost = length_m * penalty (đi được nhưng khó)
    - Ngập >= FLOOD_BLOCK_DEPTH: cost = infinity (không đi được)

    Args:
        length_m          : Chiều dài đoạn đường (mét)
        flood_depth_m     : Độ sâu ngập (mét)
        max_depth_allowed : Ngưỡng ngập tối đa cho phép đi qua

    Returns:
        Chi phí thực tế (float), math.inf nếu bị chặn
    """
    if flood_depth_m >= FLOOD_BLOCK_DEPTH:
        return math.inf                              # Chặn hoàn toàn
    if flood_depth_m > max_depth_allowed:
        return length_m * FLOOD_PENALTY_FACTOR       # Đi nhưng bị phạt nặng
    if flood_depth_m > 0:
        penalty = 1 + (flood_depth_m / max_depth_allowed) * 2
        return length_m * penalty                    # Phạt tỷ lệ theo độ sâu
    return length_m                                  # Bình thường


def haversine_heuristic(node_a_coords: Tuple[float, float],
                         node_b_coords: Tuple[float, float]) -> float:
    """
    Heuristic A* — khoảng cách Haversine thực tế giữa 2 tọa độ GPS.
    Đảm bảo admissible (không bao giờ ước lượng quá cao).
    """
    lng1, lat1 = node_a_coords
    lng2, lat2 = node_b_coords
    R = 6371000  # Bán kính Trái Đất (mét)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi  = math.radians(lat2 - lat1)
    dlng  = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ------------------------------------------------------------------ #
#  Service chính
# ------------------------------------------------------------------ #
class DijkstraService:

    def __init__(self, db: AsyncSession):
        self.routing_repo = RoutingRepository(db)

    async def build_graph(self, scenario_mm: int,
                           max_depth_allowed: float = 0.3) -> nx.DiGraph:
        """
        Xây dựng đồ thị có hướng từ dữ liệu DB.
        Trọng số cạnh được tính theo hàm compute_edge_cost.
        """
        G = nx.DiGraph()

        # Lấy tất cả cạnh từ DB
        edges = await self.routing_repo.get_all_edges(include_blocked=True)

        # Lấy cạnh bị ngập theo kịch bản
        flooded_edges = await self.routing_repo.get_edges_in_flood_zone(scenario_mm)
        flood_map: Dict[int, float] = {e["id"]: e["flood_depth_m"] for e in flooded_edges}

        for edge in edges:
            flood_depth = flood_map.get(edge.id, 0.0)
            cost = compute_edge_cost(edge.length_m, flood_depth, max_depth_allowed)

            G.add_edge(
                edge.source, edge.target,
                weight=cost,
                length_m=edge.length_m,
                flood_depth=flood_depth,
                is_flooded=flood_depth > 0,
                edge_id=edge.id,
            )
            # Nếu không một chiều → thêm cạnh ngược
            if not edge.oneway:
                G.add_edge(
                    edge.target, edge.source,
                    weight=cost,
                    length_m=edge.length_m,
                    flood_depth=flood_depth,
                    is_flooded=flood_depth > 0,
                    edge_id=edge.id,
                )

        return G

    async def find_path(self, request: RoutingRequest) -> RoutingResponse:
        """
        Tìm đường tránh ngập từ điểm đầu đến điểm cuối.
        Sử dụng A* nếu có tọa độ node, fallback Dijkstra.
        """
        # 1. Tìm node gần nhất với điểm xuất phát và đích
        start_node = await self.routing_repo.get_nearest_node(
            request.start.longitude, request.start.latitude
        )
        end_node = await self.routing_repo.get_nearest_node(
            request.end.longitude, request.end.latitude
        )

        if not start_node or not end_node:
            return RoutingResponse(
                found=False, total_distance_m=0, total_time_min=0,
                segments=[], geojson={}, flood_avoided=False,
                warnings=["Không tìm thấy đường gần điểm xuất phát hoặc đích"],
            )

        # 2. Xây đồ thị
        G = await self.build_graph(
            scenario_mm=request.scenario_mm or 100,
            max_depth_allowed=request.max_depth_m,
        )

        # 3. Chạy A*
        try:
            node_coords: Dict[int, Tuple[float, float]] = {}
            # Heuristic dựa trên tọa độ node đích
            end_coords = (end_node.lng, end_node.lat)

            def heuristic(u, v):
                u_coords = node_coords.get(u, end_coords)
                return haversine_heuristic(u_coords, end_coords)

            path_nodes = nx.astar_path(
                G, start_node.id, end_node.id,
                heuristic=heuristic, weight="weight"
            )
        except nx.NetworkXNoPath:
            return RoutingResponse(
                found=False, total_distance_m=0, total_time_min=0,
                segments=[], geojson={}, flood_avoided=False,
                warnings=["Không tìm được tuyến đường — toàn bộ đường có thể đã bị ngập"],
            )

        # 4. Tính tổng chi phí và xây response
        total_dist = 0.0
        flood_avoided = False
        segments: List[RouteSegment] = []
        coords_line: List[Tuple[float, float]] = []

        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i + 1]
            edge_data = G[u][v]
            total_dist += edge_data["length_m"]
            if edge_data["is_flooded"]:
                flood_avoided = True

        total_time_min = (total_dist / 1000) / 30 * 60  # 30 km/h trung bình

        return RoutingResponse(
            found=True,
            total_distance_m=round(total_dist, 1),
            total_time_min=round(total_time_min, 1),
            segments=segments,
            geojson={"type": "LineString", "coordinates": coords_line},
            flood_avoided=flood_avoided,
        )

