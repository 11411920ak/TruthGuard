"""Unit tests for Video Verification Engine (Phase 10)."""

import os
import tempfile
import cv2
import numpy as np
import pytest
from app.analyzers.video_analyzer import (
    analyze_video_sensationalism,
    extract_keyframes_and_text,
    analyze_video_content,
)


def create_test_video_bytes(text: str = "Government Scholarship Scheme 2026", duration_frames: int = 20) -> bytes:
    """Helper to generate a lightweight synthetic MP4 video in memory."""
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"test_vid_{os.getpid()}.mp4")

    width, height = 400, 200
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_path, fourcc, 10.0, (width, height))

    for i in range(duration_frames):
        # White background frame
        frame = np.full((height, width, 3), 255, dtype=np.uint8)
        # Put black text
        cv2.putText(
            frame,
            text[:25],
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        out.write(frame)

    out.release()

    with open(temp_path, "rb") as f:
        data = f.read()

    try:
        os.remove(temp_path)
    except Exception:
        pass

    return data


def test_analyze_video_sensationalism():
    text = "SHOCKING SECRET: Doctors banned this miracle cure! Guaranteed profit within 24 hours."
    res = analyze_video_sensationalism(text)
    assert res["sensationalism_level"] == "HIGH"
    assert res["sensationalism_score"] >= 50.0
    assert len(res["signals"]) >= 2


def test_analyze_video_sensationalism_normal():
    text = "Ministry of Education publishes updated curriculum guidelines for senior secondary schools."
    res = analyze_video_sensationalism(text)
    assert res["sensationalism_level"] == "LOW"
    assert res["sensationalism_score"] == 0.0


@pytest.mark.asyncio
async def test_extract_keyframes_and_text():
    vid_bytes = create_test_video_bytes("Urgent Scheme Alert", duration_frames=15)
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"test_meta_{os.getpid()}.mp4")
    with open(temp_path, "wb") as f:
        f.write(vid_bytes)

    try:
        res = await extract_keyframes_and_text(temp_path, max_keyframes=3)
        assert res["duration"] > 0
        assert res["fps"] == 10.0
        assert res["resolution"] == "400x200"
        assert res["keyframes_sampled"] > 0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@pytest.mark.asyncio
async def test_analyze_video_content_end_to_end():
    vid_bytes = create_test_video_bytes("Prime Minister Laptop 2026", duration_frames=10)
    res = await analyze_video_content(vid_bytes, "pm_laptop_reel.mp4")

    assert "verdict" in res
    assert "risk_score" in res
    assert "confidence" in res
    assert "video_details" in res
    assert res["video_details"]["duration"] > 0
    assert res["video_details"]["resolution"] == "400x200"
    assert len(res["reasons"]) > 0
