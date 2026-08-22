"""Contract tests for GET /api/anomalies endpoint.

Tests run against a real in-memory SQLite DB with real AnomalyDetector logic.
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
) -> Transaction:
    """Return a detached Transaction row ready for db.add()."""
    t = Transaction()
    t.user_id = user_id
    t.source = source
    t.source_id = f"{source}_{merchant}_{amount}_{date.isoformat()}"
    t.type = TransactionType.CARD_SPEND
    t.amount = amount
    t.currency = "VND"
    t.description = f"Purchase at {merchant}"
    t.merchant_name = merchant
    t.category = None
    t.transaction_date = date
    t.created_at = datetime.utcnow()
    t.email_match_status = None
    t.is_flagged = False
    t.alert_level = None
    t.alert_reason = None
    t.is_subscription = False
    t.subscription_name = None
    t.next_charge_date = None
    t.dispute_deadline = None
    t.masked_card = "4242"
    return t


async def _register_and_get_token(ac: AsyncClient, suffix: str) -> tuple[int, str]:
    """Register a unique user and return (user_id, access_token)."""
    email = f"anomaly.test.{suffix}@example.com"
    r = await ac.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": f"Test User {suffix}",
        },
    )
    assert r.status_code == 201, f"Registration failed: {r.status_code} {r.text}"
    data = r.json()
    token: str = data["access_token"]
    # Decode token sub claim (user_id) — simplest approach is to query the DB
    return email, token


# ---------------------------------------------------------------------------
# Test 1 — empty when no transactions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_anomalies_empty_when_no_transactions(transport, test_session_maker_fixture):
    """A registered user with zero transactions gets an empty list."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email, token = await _register_and_get_token(ac, "empty")

        r = await ac.get(
            "/api/anomalies",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json() == [], f"Expected empty list, got {r.json()}"


# ---------------------------------------------------------------------------
# Test 2 — duplicate charge detected
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_duplicate_charge_detected(transport, test_session_maker_fixture):
    """Two identical GrabFood charges within 24 hours produce a duplicate anomaly."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email, token = await _register_and_get_token(ac, "dupes")

        # Look up user_id from the DB (the token sub claim is the email string)
        from src.models.user import User
        from sqlalchemy import select
        async with test_session_maker_fixture() as db:
            res = await db.execute(select(User).where(User.email == email))
            user: User = res.scalar_one()
            user_id = user.id

        # Seed two identical transactions 12 hours apart
        base = datetime.utcnow() - timedelta(days=1)
        t1 = _build_tx(user_id=user_id, amount=85000.0, merchant="GrabFood", date=base)
        t2 = _build_tx(user_id=user_id, amount=85000.0, merchant="GrabFood", date=base + timedelta(hours=12))

        async with test_session_maker_fixture() as db:
            db.add(t1)
            db.add(t2)
            await db.commit()

        r = await ac.get(
            "/api/anomalies",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    assert len(body) >= 1, f"Expected at least 1 anomaly, got {body}"

    dupes = [a for a in body if a["type"] == "duplicate"]
    assert len(dupes) >= 1, f"No duplicate anomaly found in {body}"
    assert dupes[0]["severity"] == "needs_confirmation", (
        f"Expected severity 'needs_confirmation', got '{dupes[0]['severity']}'"
    )


# ---------------------------------------------------------------------------
# Test 3 — recurring subscription detected
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_recurring_subscription_detected(transport, test_session_maker_fixture):
    """Four Netflix charges 28 days apart produce a subscription anomaly."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email, token = await _register_and_get_token(ac, "sub")

        async with test_session_maker_fixture() as db:
            from src.models.user import User
            from sqlalchemy import select
            res = await db.execute(select(User).where(User.email == email))
            user: User = res.scalar_one()
            user_id = user.id

        # Seed 4 transactions 28 days apart, amount = -260000 VND
        base = datetime.utcnow() - timedelta(days=28 * 3)
        for i in range(4):
            t = _build_tx(
                user_id=user_id,
                amount=-260000.0,
                merchant="Netflix",
                date=base + timedelta(days=28 * i),
            )
            async with test_session_maker_fixture() as db:
                db.add(t)
                await db.commit()

        r = await ac.get(
            "/api/anomalies",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    subs = [a for a in body if a["type"] == "subscription"]
    assert len(subs) >= 1, f"No subscription anomaly found in {body}"
    assert "netflix" in subs[0]["description"].lower(), (
        f"Expected 'netflix' in description, got '{subs[0]['description']}'"
    )


# ---------------------------------------------------------------------------
# Test 4 — unauthenticated returns 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_anomalies_requires_auth(transport):
    """Request without Authorization header must return 401."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/anomalies")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"
