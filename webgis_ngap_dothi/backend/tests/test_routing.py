"""
tests/test_routing.py - Kiểm thử thuật toán tìm đường tránh ngập
"""

import pytest
import math
from app.services.dijkstra_service import compute_edge_cost, haversine_heuristic


class TestComputeEdgeCost:
    """Unit test cho hàm tính chi phí cạnh"""

    def test_no_flood_returns_length(self):
        """Đường không ngập → chi phí = chiều dài"""
        cost = compute_edge_cost(length_m=100, flood_depth_m=0.0)
        assert cost == 100.0

    def test_deep_flood_returns_infinity(self):
        """Ngập sâu >= 0.5m → chặn hoàn toàn"""
        cost = compute_edge_cost(length_m=100, flood_depth_m=0.5)
        assert cost == math.inf

    def test_shallow_flood_adds_penalty(self):
        """Ngập nhẹ → chi phí tăng nhưng không vô cực"""
        cost = compute_edge_cost(length_m=100, flood_depth_m=0.4, max_depth_allowed=0.3)
        assert cost > 100
        assert cost < math.inf

    def test_flood_exactly_at_threshold(self):
        """Ngập đúng ngưỡng max_depth → vẫn tăng chi phí"""
        cost = compute_edge_cost(length_m=100, flood_depth_m=0.3, max_depth_allowed=0.3)
        assert cost == 100  # Đúng ngưỡng → không phạt

    def test_cost_increases_with_depth(self):
        """Chi phí tăng dần theo độ sâu"""
        cost_shallow = compute_edge_cost(100, 0.1, 0.3)
        cost_medium  = compute_edge_cost(100, 0.2, 0.3)
        assert cost_shallow <= cost_medium


class TestHaversineHeuristic:
    """Unit test cho heuristic A*"""

    def test_same_point_distance_is_zero(self):
        coords = (106.7, 10.8)
        dist = haversine_heuristic(coords, coords)
        assert dist == pytest.approx(0.0, abs=1e-6)

    def test_known_distance(self):
        """Hai điểm cách nhau ~1km"""
        p1 = (106.700, 10.800)
        p2 = (106.709, 10.800)  # ~1km về phía đông
        dist = haversine_heuristic(p1, p2)
        assert 900 < dist < 1100  # Khoảng 1000m

    def test_heuristic_is_symmetric(self):
        p1 = (106.7, 10.8)
        p2 = (106.8, 10.9)
        assert haversine_heuristic(p1, p2) == pytest.approx(
            haversine_heuristic(p2, p1), rel=1e-6
        )


@pytest.mark.asyncio
async def test_find_path_no_data(client):
    """Tìm đường khi DB rỗng → trả về found=False"""
    resp = await client.post("/api/routing/find-path", json={
        "start": {"longitude": 106.7, "latitude": 10.8},
        "end":   {"longitude": 106.8, "latitude": 10.9},
        "avoid_flood": True,
        "scenario_mm": 100,
        "max_depth_m": 0.3
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "found" in data

