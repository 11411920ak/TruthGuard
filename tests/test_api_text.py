"""Integration tests for Text & Claim Verification API (Phase 6)."""

import pytest
import httpx
from app.main import app
from app.models.database import init_db
from app.config import get_settings


@pytest.mark.asyncio
async def test_api_analyze_text_multi_claim():
    """Verify API decomposes text into atomic claims and returns extracted entities."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "content": "Government launches Scheme X. Students will receive ₹50,000. Applications open tomorrow."
        }
        post_resp = await client.post("/api/analyze/text", json=payload)
        assert post_resp.status_code == 200
        data = post_resp.json()
        analysis_id = data["id"]
        assert data["status"] == "completed"

        # Fetch result
        get_resp = await client.get(f"/api/results/{analysis_id}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert result["input_type"] == "text"
        assert len(result["claims"]) == 3

        # Verify claim 2 has the monetary entity
        claim_texts = [c["claim_text"] for c in result["claims"]]
        assert any("₹50,000" in t for t in claim_texts)

        # Verify entities are present
        all_entities = []
        for c in result["claims"]:
            all_entities.extend(c.get("entities", []))
        assert any("₹50,000" in e for e in all_entities)


@pytest.mark.asyncio
async def test_api_analyze_text_single_scholarship_claim():
    """Verify single scholarship claim extracts entities and category."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "content": "Government announces ₹50,000 scholarship for every college student."
        }
        post_resp = await client.post("/api/analyze/text", json=payload)
        assert post_resp.status_code == 200
        data = post_resp.json()

        get_resp = await client.get(f"/api/results/{data['id']}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert len(result["claims"]) >= 1
        claim = result["claims"][0]
        assert claim["claim_type"] in ("education & scholarship", "government announcement")
        assert any("₹50,000" in e for e in claim["entities"])
