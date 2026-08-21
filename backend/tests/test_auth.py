import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/register",
            json={
                "email": "nguyen.van.a@example.com",
                "password": "SecurePassword123!",
                "full_name": "Nguyễn Văn A",
                "phone": "0912345678",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "nguyen.van.a@example.com"
    assert data["user"]["full_name"] == "Nguyễn Văn A"
    assert data["user"]["role"] == "user"


@pytest.mark.asyncio
async def test_register_duplicate_email(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # First registration
        await ac.post(
            "/api/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "Password123!",
                "full_name": "User 1",
            },
        )
        # Duplicate registration
        response = await ac.post(
            "/api/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "OtherPassword123!",
                "full_name": "User 2",
            },
        )
    assert response.status_code == 400
    assert "đã được sử dụng" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register user first
        await ac.post(
            "/api/auth/register",
            json={
                "email": "login.test@example.com",
                "password": "MySecretPassword123!",
                "full_name": "Login Tester",
            },
        )

        # Login
        response = await ac.post(
            "/api/auth/login",
            json={
                "email": "login.test@example.com",
                "password": "MySecretPassword123!",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login.test@example.com"


@pytest.mark.asyncio
async def test_login_invalid_password(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post(
            "/api/auth/register",
            json={
                "email": "wrong.pwd@example.com",
                "password": "CorrectPassword123!",
            },
        )
        response = await ac.post(
            "/api/auth/login",
            json={
                "email": "wrong.pwd@example.com",
                "password": "WrongPassword999!",
            },
        )
    assert response.status_code == 401
    assert "Email hoặc mật khẩu không chính xác" in response.json()["detail"]


@pytest.mark.asyncio
async def test_google_auth_flow(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/google",
            json={
                "email": "google.user@gmail.com",
                "full_name": "Google User",
                "google_id": "google-123456",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "google.user@gmail.com"
    assert data["user"]["full_name"] == "Google User"


@pytest.mark.asyncio
async def test_get_me_protected_endpoint(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register user
        reg_res = await ac.post(
            "/api/auth/register",
            json={
                "email": "profile.user@example.com",
                "password": "Password123!",
                "full_name": "Profile User",
            },
        )
        token = reg_res.json()["access_token"]

        # Call /me with valid token
        response = await ac.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "profile.user@example.com"
        assert response.json()["full_name"] == "Profile User"

        # Call /me without token
        unauth_res = await ac.get("/api/auth/me")
        assert unauth_res.status_code == 401

        # Call /me with invalid token
        invalid_res = await ac.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert invalid_res.status_code == 401


@pytest.mark.asyncio
async def test_forgot_password(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/forgot-password",
            json={"email": "any.email@example.com"},
        )
    assert response.status_code == 200
    assert response.json()["success"] is True
