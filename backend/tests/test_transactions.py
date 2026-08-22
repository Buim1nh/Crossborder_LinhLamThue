import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(transport):
    """Test health check endpoint."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(transport):
    """Test root endpoint."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "Wealify" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_transactions_empty(transport):
    """Test getting transactions when database is empty."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register user to obtain access token
        reg_res = await client.post(
            "/api/auth/register",
            json={
                "email": "tx_empty_test@example.com",
                "password": "Password123!",
                "full_name": "Test User",
            },
        )
        token = reg_res.json()["access_token"]
        response = await client.get(
            "/api/transactions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["transactions"] == []
