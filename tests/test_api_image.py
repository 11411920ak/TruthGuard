"""Integration tests for Image & Screenshot Verification API (Phase 8)."""

import io
import pytest
import httpx
from PIL import Image, ImageDraw

from app.main import app
from app.models.database import init_db
from app.config import get_settings


def create_test_png(text: str = "Government issues urgent advisory") -> bytes:
    """Helper to generate in-memory PNG."""
    img = Image.new("RGB", (500, 150), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 60), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_api_analyze_image_upload_and_results():
    """Verify multipart file upload to /api/analyze/image creates analysis and returns OCR details."""
    settings = get_settings()
    await init_db(settings.database_url)

    png_bytes = create_test_png("Fake Lottery Scheme win ₹1,00,000 now")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # POST multipart image
        files = {
            "file": ("lottery_screenshot.png", png_bytes, "image/png")
        }
        post_resp = await client.post("/api/analyze/image", files=files)
        assert post_resp.status_code == 200
        data = post_resp.json()

        analysis_id = data["id"]
        assert data["status"] == "completed"

        # GET results
        get_resp = await client.get(f"/api/results/{analysis_id}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert result["input_type"] == "image"
        assert "verdict" in result
        assert result["verdict"] in ["LIKELY_TRUE", "LIKELY_FALSE", "SUSPICIOUS", "UNVERIFIED"]
        assert "risk_score" in result
        assert "confidence" in result
        assert "sources" in result
        assert "reasons" in result
        assert "ocr_text" in result
