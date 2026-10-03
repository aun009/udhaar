"""API endpoint tests (mock/heuristic mode)."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

os.environ["UDHAAR_MOCK"] = "1"
os.environ["UDHAAR_DB"] = str(Path(__file__).parent / "_test_udhaar.db")

from app import db  # noqa: E402
from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
async def client():
    p = Path(os.environ["UDHAAR_DB"])
    if p.exists():
        p.unlink()
    init_db(p)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest.mark.anyio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.anyio
async def test_parse_and_confirm_flow(client):
    r = await client.post(
        "/entry/parse",
        json={"transcript": "Ramesh ji ko 340 ka samaan diya udhaar"},
    )
    assert r.status_code == 200
    label = r.json()["label"]
    assert label["amount"] == 340
    assert label["type"] == "credit_given"

    r2 = await client.post(
        "/entry/confirm",
        json={
            "customer": label["customer"],
            "amount": 340,
            "type": "credit_given",
            "note": None,
            "raw_transcript": "test",
        },
    )
    assert r2.status_code == 200
    assert r2.json()["balance"] == 340

    r3 = await client.get("/customers")
    assert r3.status_code == 200
    assert len(r3.json()) >= 1


@pytest.mark.anyio
async def test_summary(client):
    await client.post(
        "/entry/confirm",
        json={
            "customer": "Demo ji",
            "amount": 100,
            "type": "credit_given",
        },
    )
    s = (await client.get("/summary")).json()
    assert "total_outstanding" in s
    assert "top_dues" in s


@pytest.mark.anyio
async def test_reminders(client):
    await client.post(
        "/entry/confirm",
        json={"customer": "Recent due", "amount": 100, "type": "credit_given"},
    )
    assert (await client.get("/reminders")).json() == []

    old_timestamp = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    with db.connect() as conn:
        conn.execute("UPDATE entries SET created_at = ?", (old_timestamp,))

    r = await client.get("/reminders")
    assert r.status_code == 200
    assert [item["name"] for item in r.json()] == ["Recent due"]
