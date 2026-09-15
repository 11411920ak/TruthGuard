"""Integration tests for Dashboard & History Analytics API (Phase 11)."""

import pytest
import httpx
from app.main import app
from app.models.database import init_db
from app.config import get_settings


@pytest.mark.asyncio
async def test_api_history_stats():
    """Verify GET /api/history/stats returns aggregated metrics."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Fetch stats
        resp = await client.get("/api/history/stats")
        assert resp.status_code == 200
        stats = resp.json()

        assert "total_scans" in stats
        assert "verdict_counts" in stats
        assert "type_counts" in stats
        assert "avg_confidence" in stats
        assert "avg_risk_score" in stats
        assert "recent_threats" in stats
        assert isinstance(stats["recent_threats"], list)


@pytest.mark.asyncio
async def test_api_history_filtering():
    """Verify GET /api/history filters by verdict and input type."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Filter by verdict
        resp = await client.get("/api/history?verdict=LIKELY_FALSE")
        assert resp.status_code == 200
        data = resp.json()
        assert "analyses" in data
        for item in data["analyses"]:
            assert item["verdict"] == "LIKELY_FALSE"
            assert "risk_score" in item

        # Filter by search
        search_resp = await client.get("/api/history?search=laptop")
        assert search_resp.status_code == 200
        search_data = search_resp.json()
        assert "analyses" in search_data
