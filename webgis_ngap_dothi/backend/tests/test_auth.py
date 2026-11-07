"""
tests/test_auth.py - Kiểm thử xác thực và phân quyền
"""

import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    """Đăng ký tài khoản mới thành công"""
    resp = await client.post("/api/auth/register", json={
        "username":  "newuser",
        "email":     "newuser@test.com",
        "password":  "password123",
        "full_name": "Người Dùng Mới",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["role"] == "user"
    assert "hashed_password" not in data  # Không lộ mật khẩu


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    """Đăng ký trùng username → 400"""
    payload = {"username": "dupuser", "email": "dup@test.com", "password": "pass123"}
    await client.post("/api/auth/register", json=payload)
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    """Đăng nhập đúng thông tin → trả về token"""
    await client.post("/api/auth/register", json={
        "username": "loginuser", "email": "login@test.com", "password": "mypass123"
    })
    resp = await client.post("/api/auth/login", data={
        "username": "loginuser", "password": "mypass123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Sai mật khẩu → 401"""
    resp = await client.post("/api/auth/login", data={
        "username": "admin", "password": "wrongpass"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client, user_token):
    """Lấy thông tin người dùng hiện tại"""
    resp = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 200
    assert "username" in resp.json()


@pytest.mark.asyncio
async def test_access_without_token(client):
    """Truy cập route cần auth mà không có token → 401"""
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401

