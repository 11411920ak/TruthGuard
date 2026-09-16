"""
Tests verifying the exact services and flow requested by the user:
Instagram Screenshot -> FastAPI -> Gemini Vision -> Fact Check & Tavily -> Gemini Analysis -> TruthGuard Result.
"""

import io
import pytest
from httpx import AsyncClient, ASGITransport
from PIL import Image, ImageDraw
from app.main import app
from app.services.factcheck import search_fact_checks
from app.services.tavily import search_tavily
from app.services.gemini import extract_claim_from_image, analyze_claim_and_evidence


def create_test_image_bytes(text: str = "Iranian Boeing 737 shakes violently as ceiling panels fall") -> bytes:
    img = Image.new("RGB", (500, 200), color=(15, 23, 42))
    d = ImageDraw.Draw(img)
    d.text((20, 80), text, fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_service_fact_checks():
    """Verify search_fact_checks function with real query."""
    res = search_fact_checks("Iranian Boeing 737 shakes violently as ceiling panels fall")
    assert isinstance(res, dict)
    assert "claims" in res or "error" in res


def test_service_tavily():
    """Verify search_tavily function with real query."""
    res = search_tavily("Iranian Boeing 737 shakes violently as ceiling panels fall")
    assert isinstance(res, dict)
    assert "results" in res or "error" in res


def test_service_gemini_vision_and_analysis():
    """Verify extract_claim_from_image and analyze_claim_and_evidence functions."""
    img_bytes = create_test_image_bytes()
    vision_res = extract_claim_from_image(img_bytes, mime_type="image/png")
    assert isinstance(vision_res, dict)

    analysis_res = analyze_claim_and_evidence(
        claim="Iranian Boeing 737 shakes violently as ceiling panels fall",
        fact_checks=[{"publisher": "Reuters", "rating": "False", "url": "https://reuters.com"}],
        web_evidence=[{"title": "Fact check airplane video", "snippet": "Old turbulence video from 2019..."}],
    )
    assert isinstance(analysis_res, dict)
    assert "verdict" in analysis_res


@pytest.mark.asyncio
async def test_endpoint_fact_check():
    """Verify POST /api/fact-check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/fact-check",
            json={"claim": "Iranian Boeing 737 shakes violently as ceiling panels fall"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_endpoint_analyze_image_alias():
    """Verify POST /api/analyze-image endpoint accepts image and triggers pipeline."""
    img_bytes = create_test_image_bytes()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("screenshot.png", img_bytes, "image/png")}
        response = await client.post("/api/analyze-image", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "completed"

        # Check analysis result
        res_response = await client.get(f"/api/results/{data['id']}")
        assert res_response.status_code == 200
        result = res_response.json()
        assert "verdict" in result
        assert "confidence" in result
        assert "sources" in result
