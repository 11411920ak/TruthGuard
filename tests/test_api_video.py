"""Integration tests for Video Verification API (Phase 10)."""

import pytest
import httpx
from app.main import app
from app.models.database import init_db
from app.config import get_settings
from tests.test_video_analyzer import create_test_video_bytes


@pytest.mark.asyncio
async def test_api_analyze_video_upload_and_results():
    """Verify multipart video upload to /api/analyze/video creates analysis and returns video_details."""
    settings = get_settings()
    await init_db(settings.database_url)

    vid_bytes = create_test_video_bytes("Breaking News Free Laptop Scheme", duration_frames=12)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("scheme_video.mp4", vid_bytes, "video/mp4")
        }
        post_resp = await client.post("/api/analyze/video", files=files)
        assert post_resp.status_code == 200
        data = post_resp.json()
        analysis_id = data["id"]
        assert data["status"] == "completed"

        # GET results
        get_resp = await client.get(f"/api/results/{analysis_id}")
        assert get_resp.status_code == 200
        result = get_resp.json()

        assert result["input_type"] == "video"
        assert result["video_details"] is not None
        assert result["video_details"]["filename"] == "scheme_video.mp4"
        assert result["video_details"]["duration"] > 0
        assert result["video_details"]["resolution"] == "400x200"
        assert result["verdict"] in ("LIKELY_TRUE", "LIKELY_FALSE", "SUSPICIOUS", "UNVERIFIED")
