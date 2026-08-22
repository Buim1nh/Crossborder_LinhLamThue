"""Tests for the subscription detection endpoints.

These are skipped when no model has been promoted to ml/registry — run
`python -m ml.cli train --promote` from the repository root first.
"""
import csv
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.services.subscription_model import is_available

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN = REPO_ROOT / "subscription_labels.csv"

needs_model = pytest.mark.skipif(not is_available(), reason="no promoted model")


def _sample_rows(n: int = 8) -> list[dict]:
    with open(GOLDEN, newline="", encoding="utf-8-sig") as f:
        rows = [row for _, row in zip(range(n), csv.DictReader(f))]
    for r in rows:
        r.pop("label", None)
    return rows


async def _register_and_get_token(c: AsyncClient) -> str:
    """Register a test user and return a valid bearer token."""
    import uuid
    email = f"subtest.{uuid.uuid4().hex[:8]}@example.com"
    reg = await c.post("/api/auth/register", json={
        "email": email,
        "password": "TestPass123!",
        "full_name": "Subscription Test User",
    })
    return reg.json()["access_token"]


@pytest.mark.asyncio
@needs_model
async def test_model_info():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        token = await _register_and_get_token(c)
        r = await c.get("/api/subscriptions/model",
                        headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["version"].startswith("v")
    assert 0.0 <= body["threshold"] <= 1.0
    assert body["feature_mode"] == "robust"


@pytest.mark.asyncio
@needs_model
@pytest.mark.skipif(not GOLDEN.exists(), reason="golden dataset missing")
async def test_score_batch():
    rows = _sample_rows()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        token = await _register_and_get_token(c)
        r = await c.post("/api/subscriptions/score", json={"transactions": rows},
                          headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["n_scored"] == len(rows)
    assert len(body["results"]) == len(rows)
    for res in body["results"]:
        assert 0.0 <= res["subscription_proba"] <= 1.0
        assert res["is_subscription"] in (0, 1)
        assert res["model_version"] == body["model_version"]


@pytest.mark.asyncio
@needs_model
@pytest.mark.skipif(not GOLDEN.exists(), reason="golden dataset missing")
async def test_score_respects_threshold_override():
    rows = _sample_rows()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        token = await _register_and_get_token(c)
        low = await c.post("/api/subscriptions/score",
                           json={"transactions": rows, "threshold": 0.0},
                           headers={"Authorization": f"Bearer {token}"})
        high = await c.post("/api/subscriptions/score",
                            json={"transactions": rows, "threshold": 1.0},
                            headers={"Authorization": f"Bearer {token}"})
    assert low.json()["n_subscription"] == len(rows)
    assert high.json()["n_subscription"] == 0


@pytest.mark.asyncio
async def test_score_rejects_empty_batch():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        token = await _register_and_get_token(c)
        r = await c.post("/api/subscriptions/score", json={"transactions": []},
                         headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400


@pytest.mark.asyncio
@needs_model
async def test_score_rejects_bad_schema():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        token = await _register_and_get_token(c)
        r = await c.post("/api/subscriptions/score",
                         json={"transactions": [{"khong_phai_giao_dich": 1}]},
                         headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_score_requires_auth():
    """Verify /api/subscriptions/score is protected by auth — no model needed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        resp = await c.post("/api/subscriptions/score",
                            json={"transactions": [{"Loai_giao_dich": "Top Up", "So_tien": 260000}]})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_model_info_requires_auth():
    """Verify /api/subscriptions/model is protected by auth — no model needed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        resp = await c.get("/api/subscriptions/model")
    assert resp.status_code == 401
