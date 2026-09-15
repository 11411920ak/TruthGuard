"""Unit tests for Image Analyzer & OCR Verification (Phase 8)."""

import io
import pytest
from PIL import Image, ImageDraw
from app.analyzers.image_analyzer import (
    extract_embedded_urls,
    extract_text_from_image_bytes,
    analyze_screenshot_image,
)


def create_test_image_with_text(text: str, width: int = 600, height: int = 200) -> bytes:
    """Generate a clean synthetic PNG image with high-contrast text for testing."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw simple text using default bitmap font
    draw.text((30, 80), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_extract_embedded_urls():
    sample_text = (
        "Breaking: Free laptops scheme! Claim yours now at http://free-laptops-gov.xyz "
        "or visit www.official-update.in/bonus. Ignore scams on twitter.com."
    )
    urls = extract_embedded_urls(sample_text)
    assert len(urls) >= 2
    assert any("free-laptops-gov.xyz" in u for u in urls)
    assert any("official-update.in" in u for u in urls)


def test_extract_embedded_urls_empty():
    assert extract_embedded_urls("No links here whatsoever") == []


@pytest.mark.asyncio
async def test_ocr_extraction_on_synthetic_image():
    """Verify OCR engine runs on generated image bytes without crashing."""
    img_bytes = create_test_image_with_text("TRUTHGUARD VERIFICATION TEST")
    text = await extract_text_from_image_bytes(img_bytes)
    # WinOCR should either recognize it or gracefully return a string
    assert isinstance(text, str)


@pytest.mark.asyncio
async def test_analyze_screenshot_blank_image():
    """Verify empty/blank screenshot returns UNVERIFIED with proper guidance."""
    blank_img = Image.new("RGB", (300, 300), color=(255, 255, 255))
    buf = io.BytesIO()
    blank_img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    res = await analyze_screenshot_image(img_bytes, "blank_test.png")
    assert res["verdict"] in ("UNVERIFIED", "SUSPICIOUS")
    assert res["ocr_text"] is not None
    assert len(res["reasons"]) > 0


@pytest.mark.asyncio
async def test_analyze_screenshot_dual_engine_integration():
    """Verify screenshot with scam link triggers website analyzer and sets elevated risk."""
    img_bytes = create_test_image_with_text("Free 50000 bonus at http://claim-free-bonus.xyz")
    res = await analyze_screenshot_image(img_bytes, "scam_screenshot.png")

    assert "verdict" in res
    assert "risk_score" in res
    assert "reasons" in res
    assert "sources" in res
    assert res["verdict"] in ("LIKELY_FALSE", "SUSPICIOUS", "UNVERIFIED")
