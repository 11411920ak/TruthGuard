"""Integration tests for Cross-Source Verification & UNVERIFIED API (Phase 7)."""

import pytest
import httpx
from app.main import app
from app.models.database import init_db
from app.config import get_settings


@pytest.mark.asyncio
async def test_api_fake_scheme_contradiction():
    """Verify API handles viral misinformation and returns LIKELY_FALSE with proof sources."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"content": "Government is giving free laptops to every student across India."}
        post_resp = await client.post("/api/analyze/text", json=payload)
        assert post_resp.status_code == 200
        data = post_resp.json()

        get_resp = await client.get(f"/api/results/{data['id']}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert result["verdict"] == "LIKELY_FALSE"
        assert result["risk_score"] >= 75.0
        assert len(result["sources"]) >= 2
        # Verify sources have reliability
        assert any(s["reliability"] >= 0.85 for s in result["sources"])
        # Verify reasons contain contradiction
        assert any(r["type"] == "contradiction" for r in result["reasons"])


@pytest.mark.asyncio
async def test_api_unverified_handling():
    """Verify API distinguishes FALSE from UNVERIFIED when evidence is absent/insufficient."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"content": "A secret tunnel was supposedly located behind a local shop in town yesterday."}
        post_resp = await client.post("/api/analyze/text", json=payload)
        assert post_resp.status_code == 200
        data = post_resp.json()

        get_resp = await client.get(f"/api/results/{data['id']}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert result["verdict"] == "UNVERIFIED"
        assert result["confidence"] <= 60.0
        assert any("insufficient" in r["text"].lower() or "unverified" in r["text"].lower() for r in result["reasons"])
