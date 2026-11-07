"""
tests/test_reports.py - Kiểm thử CRUD báo cáo ngập
"""

import pytest


@pytest.mark.asyncio
async def test_submit_report_requires_auth(client):
    """Gửi báo cáo không có token → 401"""
    resp = await client.post("/api/reports/", json={
        "longitude": 106.7, "latitude": 10.8,
        "description": "Ngập nặng tại đây"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_submit_report_success(client, user_token):
    """Gửi báo cáo có token hợp lệ → 201"""
    resp = await client.post(
        "/api/reports/",
        json={"longitude": 106.7, "latitude": 10.8, "description": "Test ngập"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert data["longitude"] == pytest.approx(106.7)


@pytest.mark.asyncio
async def test_list_reports_requires_admin(client, user_token):
    """User thường không xem được danh sách tất cả báo cáo"""
    resp = await client.get(
        "/api/reports/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_reports_as_admin(client, admin_token):
    """Admin lấy danh sách báo cáo thành công"""
    resp = await client.get(
        "/api/reports/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "reports" in data


@pytest.mark.asyncio
async def test_my_reports(client, user_token):
    """User xem báo cáo của mình"""
    resp = await client.get(
        "/api/reports/my",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_review_report(client, admin_token, user_token):
    """Admin duyệt báo cáo → status chuyển verified"""
    # Tạo báo cáo
    create = await client.post(
        "/api/reports/",
        json={"longitude": 106.7, "latitude": 10.8, "description": "Ngập test"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    report_id = create.json()["id"]

    # Admin duyệt
    resp = await client.patch(
        f"/api/reports/{report_id}/review",
        json={"status": "verified", "review_note": "Đã xác minh tại thực địa"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "verified"

