"""Integration tests for TruthGuard URL Analysis API."""

import pytest
import httpx
from app.main import app
from app.models.database import init_db
from app.config import get_settings


@pytest.mark.asyncio
async def test_api_analyze_url_ssrf_blocking():
    """Verify API blocks SSRF target and saves appropriate critical risk result."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Submit SSRF target
        post_resp = await client.post("/api/analyze/url", json={"url": "http://127.0.0.1:8080/admin"})
        assert post_resp.status_code == 200
        data = post_resp.json()
        analysis_id = data["id"]
        assert data["status"] == "completed"

        # Fetch result
        get_resp = await client.get(f"/api/results/{analysis_id}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert result["verdict"] == "LIKELY_FALSE"
        assert result["risk_score"] >= 90.0
        assert result["website_details"] is not None
        assert "127.0.0.1" in result["website_details"]["domain"]
        assert any("SSRF" in s or "Security" in s or "private" in s.lower() for s in result["website_details"]["signals"])


@pytest.mark.asyncio
async def test_api_analyze_url_legitimate():
    """Verify API analyzes legitimate domain and produces detailed breakdown."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        post_resp = await client.post("/api/analyze/url", json={"url": "https://wikipedia.org"})
        assert post_resp.status_code == 200
        data = post_resp.json()
        analysis_id = data["id"]

        get_resp = await client.get(f"/api/results/{analysis_id}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert result["verdict"] == "LIKELY_TRUE"
        assert result["risk_score"] <= 25.0
        assert result["website_details"] is not None
        assert result["website_details"]["https"] is True
        assert "wikipedia.org" in result["website_details"]["domain"]
        assert len(result["sources"]) >= 2
        assert len(result["reasons"]) >= 1
