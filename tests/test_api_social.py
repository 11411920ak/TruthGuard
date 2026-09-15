"""Integration tests for Social Media Verification API (Phase 9)."""

import pytest
import httpx
from app.main import app
from app.models.database import init_db
from app.config import get_settings


@pytest.mark.asyncio
async def test_api_analyze_viral_whatsapp_forward():
    """Verify posting a viral forward triggers social analysis and returns social_details."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "content": (
                "Forwarded many times: URGENT! Government offering free laptops to all college students. "
                "Apply immediately before midnight at http://scam-laptop-portal.top. Share to 10 friends!"
            )
        }
        post_resp = await client.post("/api/analyze/text", json=payload)
        assert post_resp.status_code == 200
        data = post_resp.json()
        analysis_id = data["id"]

        # GET results
        get_resp = await client.get(f"/api/results/{analysis_id}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert result["input_type"] == "social"
        assert result["verdict"] in ("LIKELY_FALSE", "SUSPICIOUS")
        assert result["social_details"] is not None
        assert result["social_details"]["platform"] == "WhatsApp Forward"
        assert result["social_details"]["manipulation_level"] in ("HIGH", "MEDIUM")
        assert len(result["social_details"]["manipulation_signals"]) >= 1


@pytest.mark.asyncio
async def test_api_analyze_twitter_spoof_post():
    """Verify spoofed Twitter account post flags impersonation."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "content": "RT @RBI_support_official: Claim your ₹25,000 KYC refund instantly. #RBIBonus"
        }
        post_resp = await client.post("/api/analyze/text", json=payload)
        assert post_resp.status_code == 200
        data = post_resp.json()
        analysis_id = data["id"]

        get_resp = await client.get(f"/api/results/{analysis_id}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert result["input_type"] == "social"
        assert result["social_details"] is not None
        assert result["social_details"]["platform"] == "Twitter / X"
        assert result["social_details"]["impersonation_risk"] in ("HIGH", "MEDIUM")
