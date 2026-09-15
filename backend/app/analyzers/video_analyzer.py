"""Video Verification & Multi-Modal Forensics Engine for TruthGuard.

Performs:
1. Video container and metadata extraction (resolution, duration, FPS, frame count).
2. Temporal keyframe sampling across video duration via OpenCV.
3. On-screen text & subtitle OCR extraction on sampled keyframes using Windows Native OCR.
4. Embedded URL, QR code text, and scheme link detection.
5. Sensationalism & synthetic media risk analysis (clickbait cues, artificial urgency, miracle tropes).
6. Dual-engine claim verification & cross-source evidence scoring.
"""

import os
import re
import cv2
import tempfile
from typing import Optional

from app.analyzers.claim_extractor import extract_claims
from app.analyzers.evidence_engine import verify_claims_and_retrieve_evidence
from app.analyzers.website_analyzer import analyze_website
from app.analyzers.image_analyzer import extract_text_from_image_bytes, extract_embedded_urls


# ── Sensationalism & Synthetic Tropes ──

SENSATIONAL_PATTERNS = [
    r"shocking (?:truth|revelation|secret)",
    r"banned by (?:govt|government|police|media)",
    r"miracle (?:cure|solution|discovery)",
    r"guaranteed (?:profit|returns|income|win)",
    r"secret (?:they|doctors|banks) don'?t want you to know",
    r"leak(?:ed)? (?:tape|video|document)",
    r"must watch before (?:it'?s deleted|midnight)",
    r"urgent (?:alert|warning|update)",
    r"100% (?:free|legit|real|working)",
]


def analyze_video_sensationalism(text: str) -> dict:
    """Detect sensationalism, clickbait claims, and synthetic manipulation signals."""
    text_lower = text.lower()
    signals = []
    score = 0.0

    for pat in SENSATIONAL_PATTERNS:
        if re.search(pat, text_lower):
            score += 25.0
            signals.append(f"Sensationalist trope detected: '{pat.replace(r'(?:', '').replace(r')', '')}'")

    normalized_score = min(100.0, score)
    level = "HIGH" if normalized_score >= 50 else ("MEDIUM" if normalized_score >= 25 else "LOW")

    return {
        "sensationalism_level": level,
        "sensationalism_score": normalized_score,
        "signals": signals,
    }


# ── Keyframe Extraction & Multi-Frame OCR ──

async def extract_keyframes_and_text(video_path: str, max_keyframes: int = 5) -> dict:
    """
    Extract metadata and sample keyframes from a video file.
    Runs Windows OCR on each sampled frame.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            "duration": 0.0,
            "fps": 0.0,
            "resolution": "Unknown",
            "frame_count": 0,
            "on_screen_text": "",
            "keyframes_sampled": 0,
            "frame_texts": [],
        }

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = round(total_frames / fps, 2) if fps > 0 else 0.0
    resolution = f"{width}x{height}"

    if total_frames <= 0:
        cap.release()
        return {
            "duration": 0.0,
            "fps": fps,
            "resolution": resolution,
            "frame_count": 0,
            "on_screen_text": "",
            "keyframes_sampled": 0,
            "frame_texts": [],
        }

    # Sample uniformly at intervals (e.g. 10%, 30%, 50%, 70%, 90%)
    sample_ratios = [0.1, 0.3, 0.5, 0.7, 0.9][:max_keyframes]
    frame_indices = [int(r * total_frames) for r in sample_ratios]

    frame_texts = []
    seen_texts = set()

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        # Encode frame as PNG in memory
        success, buffer = cv2.imencode(".png", frame)
        if not success:
            continue

        frame_bytes = buffer.tobytes()
        text = await extract_text_from_image_bytes(frame_bytes)
        clean_text = text.strip()

        if clean_text and clean_text not in seen_texts:
            seen_texts.add(clean_text)
            timestamp_sec = round(idx / fps, 1) if fps > 0 else 0.0
            frame_texts.append({
                "frame_index": idx,
                "timestamp": f"{timestamp_sec}s",
                "text": clean_text,
            })

    cap.release()

    combined_text = "\n".join(ft["text"] for ft in frame_texts)

    return {
        "duration": duration,
        "fps": round(fps, 1),
        "resolution": resolution,
        "frame_count": total_frames,
        "keyframes_sampled": len(frame_indices),
        "frame_texts": frame_texts,
        "on_screen_text": combined_text,
    }


# ── End-to-End Video Verification Orchestrator ──

async def analyze_video_content(video_bytes: bytes, filename: str) -> dict:
    """
    Main orchestrator for Video Verification:
    1. Writes video bytes to a secure temporary file.
    2. Extracts video container specs & samples keyframes.
    3. Runs OCR on keyframes to extract on-screen banners & tickers.
    4. Scans for on-screen URLs and sensationalism markers.
    5. Decomposes on-screen text into claims & verifies cross-source evidence.
    6. Combines signals into authoritative verdict and risk score.
    """
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"truthguard_vid_{os.getpid()}_{filename}")

    try:
        with open(temp_path, "wb") as f:
            f.write(video_bytes)

        # 1. Extract metadata and on-screen text
        vid_data = await extract_keyframes_and_text(temp_path)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

    on_screen_text = vid_data["on_screen_text"]
    if not on_screen_text or len(on_screen_text.strip()) < 5:
        # If no on-screen text detected, use filename or return unverified
        on_screen_text = f"Video clip '{filename}' ({vid_data['duration']}s, {vid_data['resolution']})"

    # 2. Sensationalism & Clickbait Detection
    sensationalism = analyze_video_sensationalism(on_screen_text)

    # 3. Embedded Link Scanning
    embedded_urls = extract_embedded_urls(on_screen_text)
    primary_url = embedded_urls[0] if embedded_urls else None
    website_res = None
    if primary_url:
        website_res = await analyze_website(primary_url)

    # 4. Decompose Claims and Cross-Reference Evidence
    claims_list = await extract_claims(on_screen_text)
    evidence_res = await verify_claims_and_retrieve_evidence(claims_list, on_screen_text)

    # 5. Risk & Verdict Synthesis
    verdict = evidence_res["verdict"]
    confidence = evidence_res["confidence"]
    risk_score = evidence_res["risk_score"]
    reasons = list(evidence_res["reasons"])
    sources = list(evidence_res["sources"])

    # Prepend Video Spec Context
    reasons.insert(0, {
        "type": "support",
        "text": f"Video Specs: {vid_data['duration']}s duration, {vid_data['resolution']} resolution @ {vid_data['fps']} FPS ({vid_data['keyframes_sampled']} keyframes inspected)",
    })

    # Add Sensationalism Signals
    if sensationalism["sensationalism_level"] in ("HIGH", "MEDIUM"):
        reasons.append({
            "type": "warning",
            "text": f"Sensationalism & Manipulation Risk: {sensationalism['sensationalism_level']} ({sensationalism['sensationalism_score']}/100)",
        })
        for sig in sensationalism["signals"]:
            reasons.append({"type": "contradiction", "text": sig})
        risk_score = max(risk_score, sensationalism["sensationalism_score"])

    # Factor in Embedded Website Security
    if website_res:
        sources.append({
            "name": f"On-Screen Link Scanner ({website_res['domain']})",
            "type": "security-engine",
            "url": primary_url,
            "reliability": 0.92,
        })
        if website_res["risk_level"] in ("HIGH", "CRITICAL"):
            verdict = "LIKELY_FALSE"
            risk_score = max(risk_score, website_res["risk_score"], 85.0)
            confidence = max(confidence, 90.0)
            reasons.append({
                "type": "contradiction",
                "text": f"Scam Link Detected on Screen: Embedded URL '{website_res['domain']}' flagged as {website_res['risk_level']} Risk ({website_res['risk_score']}/100)",
            })

    # Recommendation synthesis
    if verdict == "LIKELY_FALSE":
        recommendation = "🛑 DO NOT SHARE THIS VIDEO. The on-screen claims or displayed links are fraudulent or debunked by authoritative sources."
    elif verdict == "SUSPICIOUS":
        recommendation = "⚠️ SUSPICIOUS VIDEO. Elevated sensationalism or unverified claims detected. Avoid clicking on-screen links."
    elif verdict == "UNVERIFIED":
        recommendation = "🟡 UNVERIFIED: The claims shown in this video could not be corroborated by independent reporting. Treat with skepticism."
    else:
        recommendation = "✅ The factual claims identified in this video are corroborated by independent reporting."

    clean_filename = filename.replace("[Video: ", "").rstrip("]")
    video_details = {
        "filename": clean_filename,
        "duration": vid_data["duration"],
        "fps": vid_data["fps"],
        "resolution": vid_data["resolution"],
        "frame_count": vid_data["frame_count"],
        "keyframes_sampled": vid_data["keyframes_sampled"],
        "on_screen_text": on_screen_text,
        "sensationalism_level": sensationalism["sensationalism_level"],
        "sensationalism_score": sensationalism["sensationalism_score"],
        "sensationalism_signals": sensationalism["signals"],
        "embedded_url": primary_url,
    }

    return {
        "verdict": verdict,
        "confidence": confidence,
        "risk_score": risk_score,
        "evidence_coverage": evidence_res.get("evidence_coverage", 70.0),
        "video_details": video_details,
        "website_details": website_res,
        "claims": evidence_res["claims"],
        "sources": sources,
        "reasons": reasons,
        "recommendation": recommendation,
    }
