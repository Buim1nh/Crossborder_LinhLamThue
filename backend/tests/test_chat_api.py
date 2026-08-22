"""Contract tests for POST /api/chat endpoint.

Each test registers a fresh user via the API, seeds transactions directly
via SQLAlchemy, then calls /api/chat over HTTP with a real JWT token.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from src.models.transaction import Transaction, TransactionType
from src.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _register_and_get_token(ac: AsyncClient, suffix: str) -> tuple[str, str]:
    """Register a unique user and return (email, access_token)."""
    email = f"chat.test.{suffix}@example.com"
    r = await ac.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": f"Chat Test User {suffix}",
        },
    )
    assert r.status_code == 201, f"Registration failed: {r.status_code} {r.text}"
    return email, r.json()["access_token"]


async def _seed_transactions(session_maker, user_id: int) -> None:
    """Seed two transactions (income + expense) for the given user."""
    base = datetime.utcnow() - timedelta(days=7)
    txns = [
        Transaction(
            user_id=user_id,
            source="account",
            source_id=f"income_{user_id}",
            type=TransactionType.PAYIN,
            amount=5_000_000.0,
            currency="VND",
            description="Salary deposit",
            merchant_name=None,
            category=None,
            transaction_date=base,
            created_at=datetime.utcnow(),
            email_match_status=None,
            is_flagged=False,
            alert_level=None,
            alert_reason=None,
            is_subscription=False,
            subscription_name=None,
            next_charge_date=None,
            dispute_deadline=None,
            masked_card=None,
        ),
        Transaction(
            user_id=user_id,
            source="card",
            source_id=f"netflix_{user_id}",
            type=TransactionType.CARD_SPEND,
            amount=-260_000.0,
            currency="VND",
            description="Netflix subscription",
            merchant_name="Netflix",
            category=None,
            transaction_date=base + timedelta(days=5),
            created_at=datetime.utcnow(),
            email_match_status=None,
            is_flagged=False,
            alert_level=None,
            alert_reason=None,
            is_subscription=True,
            subscription_name="Netflix",
            next_charge_date=None,
            dispute_deadline=None,
            masked_card="4242",
        ),
    ]
    async with session_maker() as db:
        from sqlalchemy import select
        for t in txns:
            db.add(t)
        await db.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chat_requires_auth(transport):
    """Unauthenticated requests are rejected with 401."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/chat", json={"message": "hello"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_returns_error_model_when_llm_fails(
    transport, test_session_maker_fixture
):
    """When LLM raises an exception, the endpoint returns 200 with model='error'."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email, token = await _register_and_get_token(ac, "error_model")

        async with test_session_maker_fixture() as db:
            from sqlalchemy import select
            res = await db.execute(select(User).where(User.email == email))
            user: User = res.scalar_one()
            await _seed_transactions(test_session_maker_fixture, user.id)

        with patch("src.api.chat.get_llm_provider") as mock_llm:
            mock_llm.return_value.chat.side_effect = Exception("no API key")
            resp = await ac.post(
                "/api/chat",
                json={"message": "Tóm tắt chi tiêu"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert data["model"] == "error"


@pytest.mark.asyncio
async def test_chat_with_mocked_llm(
    transport, test_session_maker_fixture
):
    """With a working LLM mock, the endpoint returns the LLM's reply and model."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email, token = await _register_and_get_token(ac, "mocked")

        async with test_session_maker_fixture() as db:
            from sqlalchemy import select
            res = await db.execute(select(User).where(User.email == email))
            user: User = res.scalar_one()
            await _seed_transactions(test_session_maker_fixture, user.id)

        mock_resp = AsyncMock()
        mock_resp.content = "Tổng thu chi của bạn là 5 triệu đồng."
        mock_resp.model = "mock-model"

        with patch("src.api.chat.get_llm_provider") as mock_llm:
            mock_llm.return_value.chat = AsyncMock(return_value=mock_resp)
            resp = await ac.post(
                "/api/chat",
                json={"message": "Tóm tắt chi tiêu"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data["reply"] == "Tổng thu chi của bạn là 5 triệu đồng."
    assert data["model"] == "mock-model"
