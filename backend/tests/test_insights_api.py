"""Contract tests for GET /api/insights endpoint.

Tests run against a real in-memory SQLite DB with real insights logic.
Each test registers a fresh user (unique email), seeds transactions via
SQLAlchemy, then calls the endpoint over HTTP with a real JWT token.
"""
import pytest
from datetime import datetime, timedelta

from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.models.transaction import Transaction, TransactionType
from src.models.user import User
from src.core.security import create_access_token


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_tx(
    user_id: int,
    amount: float,
    merchant: str,
    date: datetime,
    source: str = "card",
    currency: str = "VND",
    is_subscription: bool = False,
) -> Transaction:
    """Return a detached Transaction row ready for db.add()."""
    t = Transaction()
    t.user_id = user_id
    t.source = source
    t.source_id = f"{source}_{merchant}_{amount}_{date.isoformat()}"
    t.type = TransactionType.CARD_SPEND
    t.amount = amount
    t.currency = currency
    t.description = f"Purchase at {merchant}"
    t.merchant_name = merchant
    t.category = None
    t.transaction_date = date
    t.created_at = datetime.utcnow()
    t.email_match_status = None
    t.is_flagged = False
    t.alert_level = None
    t.alert_reason = None
    t.is_subscription = is_subscription
    t.subscription_name = merchant if is_subscription else None
    t.next_charge_date = None
    t.dispute_deadline = None
    t.masked_card = "4242"
    return t


async def _register_and_get_token(ac: AsyncClient, suffix: str) -> tuple[str, str]:
    """Register a unique user and return (email, access_token)."""
    email = f"insights.test.{suffix}@example.com"
    r = await ac.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": f"Insights Test User {suffix}",
        },
    )
    assert r.status_code == 201, f"Registration failed: {r.status_code} {r.text}"
    data = r.json()
    token: str = data["access_token"]
    return email, token


# ---------------------------------------------------------------------------
# Test 1 — empty user returns zeroed summary
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_insights_empty_user(transport, test_session_maker_fixture):
    """A registered user with zero transactions gets zeroed summary fields."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email, token = await _register_and_get_token(ac, "empty")

        r = await ac.get(
            "/api/insights",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()

    assert body["summary"]["total_income_vnd"] == 0.0
    assert body["summary"]["total_expense_vnd"] == 0.0
    assert body["summary"]["net_vnd"] == 0.0
    assert body["summary"]["subscription_burn_vnd"] == 0.0
    assert body["summary"]["transaction_count"] == 0
    assert body["top_subscriptions"] == []
    assert body["active_anomalies"] == []
    assert body["period"]["from"] is None
    assert body["period"]["to"] is None
    assert "computed_at" in body


# ---------------------------------------------------------------------------
# Test 2 — mixed income and expense
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_insights_mixed_income_expense(transport, test_session_maker_fixture):
    """Income > 0 and expense < 0 are summed and netted correctly in VND."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email, token = await _register_and_get_token(ac, "mixed")

        async with test_session_maker_fixture() as db:
            from sqlalchemy import select
            res = await db.execute(select(User).where(User.email == email))
            user: User = res.scalar_one()
            user_id = user.id

        base = datetime.utcnow() - timedelta(days=7)
        txns = [
            _build_tx(user_id, 500_000.0, "Salary", base, "account"),
            _build_tx(user_id, -200_000.0, "Coffee Shop", base + timedelta(days=1), "card"),
            _build_tx(user_id, -100_000.0, "Grab", base + timedelta(days=2), "wallet"),
        ]
        async with test_session_maker_fixture() as db:
            for t in txns:
                db.add(t)
            await db.commit()

        r = await ac.get(
            "/api/insights",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    summary = body["summary"]

    assert summary["total_income_vnd"] == 500_000.0
    assert summary["total_expense_vnd"] == 300_000.0
    assert summary["net_vnd"] == 200_000.0
    assert summary["transaction_count"] == 3

    # by_source breakdown
    assert body["by_source"]["account"]["income_vnd"] == 500_000.0
    assert body["by_source"]["card"]["expense_vnd"] == 200_000.0
    assert body["by_source"]["wallet"]["expense_vnd"] == 100_000.0


# ---------------------------------------------------------------------------
# Test 3 — USD conversion
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_insights_usd_conversion(transport, test_session_maker_fixture):
    """Amounts in USD are converted to VND at 25,400 VND/USD."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email, token = await _register_and_get_token(ac, "usd")

        async with test_session_maker_fixture() as db:
            from sqlalchemy import select
            res = await db.execute(select(User).where(User.email == email))
            user: User = res.scalar_one()
            user_id = user.id

        base = datetime.utcnow() - timedelta(days=3)
        txns = [
            _build_tx(user_id, 100.0, "Apple", base, "card", currency="USD"),  # 100 USD = 2,540,000 VND
            _build_tx(user_id, -50.0, "Netflix", base + timedelta(days=1), "card", currency="USD", is_subscription=True),
        ]
        async with test_session_maker_fixture() as db:
            for t in txns:
                db.add(t)
            await db.commit()

        r = await ac.get(
            "/api/insights",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    summary = body["summary"]

    assert summary["total_income_vnd"] == pytest.approx(2_540_000.0, rel=1e-2)
    assert summary["total_expense_vnd"] == pytest.approx(1_270_000.0, rel=1e-2)
    assert summary["subscription_burn_vnd"] == pytest.approx(1_270_000.0, rel=1e-2)

    # Top subscriptions should include Netflix
    assert len(body["top_subscriptions"]) == 1
    assert body["top_subscriptions"][0]["merchant"] == "Netflix"


# ---------------------------------------------------------------------------
# Test 4 — unauthenticated returns 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_insights_requires_auth(transport):
    """Request without Authorization header must return 401."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/insights")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"
