"""Screenshot & Image Verification Engine for TruthGuard.

Performs:
1. Native Windows OCR text extraction on uploaded screenshots.
2. Embedded URL and domain detection.
3. Dual-engine verification: Combines claim fact-checking with website security analysis.
4. Synthesizes risk scores and generates comprehensive verification reports.
"""

import io
import re
import urllib.parse
from typing import Optional
from PIL import Image, ImageEnhance

from app.analyzers.claim_extractor import extract_claims
from app.analyzers.evidence_engine import verify_claims_and_retrieve_evidence
from app.analyzers.website_analyzer import analyze_website


# ── URL Extraction Pattern ──

EMBEDDED_URL_PATTERN = re.compile(
    r"\b(?:https?://[^\s]+|(?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]*\.(?:com|org|in|top|xyz|net|io|co|info|biz|site|buzz|cc|gov|edu|me)(?:/[^\s]*)?)\b",
    re.IGNORECASE,
)


def extract_embedded_urls(text: str) -> list[str]:
    """Scan OCR text for embedded web links, domains, and shortened URLs."""
    matches = EMBEDDED_URL_PATTERN.findall(text)
    clean_urls = []
    for m in matches:
        clean = m.strip(".,;:()[]{}'\"")
        if clean and len(clean) >= 4 and "." in clean:
            # Normalize scheme if omitted
            if not clean.startswith(("http://", "https://")):
                clean = "https://" + clean
            if clean not in clean_urls:
                clean_urls.append(clean)
    return clean_urls


# ── Native Windows OCR Engine ──

async def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """
    Extract text from raw image bytes using native Windows OCR (winocr).
    Applies image contrast enhancement if needed.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB/RGBA for winocr
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")

        # Attempt OCR
        import winocr
        result = await winocr.recognize_pil(image, "en")
        extracted_text = result.text.strip() if result and result.text else ""

        # If text is empty or very short, try contrast pre-processing
        if len(extracted_text) < 5:
            enhancer = ImageEnhance.Contrast(image.convert("L"))
            enhanced = enhancer.enhance(2.0)
            result_retry = await winocr.recognize_pil(enhanced.convert("RGBA"), "en")
            if result_retry and result_retry.text:
                extracted_text = result_retry.text.strip()

        return extracted_text

    except Exception as e:
        # Fallback if image format is corrupt or winocr fails
        return ""


# ── Dual-Engine Verification Orchestrator ──

async def analyze_screenshot_image(image_bytes: bytes, filename: str) -> dict:
    """
    Main entry point for screenshot verification.
    1. Runs OCR text extraction.
    2. Scans for embedded URLs.
    3. Analyzes embedded website security (if URL exists).
    4. Decomposes text into atomic claims and cross-references evidence.
    5. Fuses claim & website signals into an authoritative verdict.
    """
    # 1. OCR Text Extraction
    ocr_text = await extract_text_from_image_bytes(image_bytes)

    if not ocr_text or len(ocr_text.strip()) < 5:
        # Unreadable image or no text detected
        return {
            "verdict": "UNVERIFIED",
            "confidence": 30.0,
            "risk_score": 50.0,
            "evidence_coverage": 10.0,
            "ocr_text": ocr_text or "[No legible text detected in image]",
            "embedded_url": None,
            "website_details": None,
            "claims": [
                {
                    "claim_text": f"Screenshot image '{filename}' contains verifiable information",
                    "claim_type": "image authenticity",
                    "entities": [],
                    "verdict": "UNVERIFIED",
                    "confidence": 30.0,
                }
            ],
            "sources": [
                {"name": "Windows Native OCR Engine", "type": "ocr", "url": None, "reliability": 0.90}
            ],
            "reasons": [
                {"type": "warning", "text": "No clear or legible text could be extracted from the uploaded screenshot"},
                {"type": "warning", "text": "Please upload a higher-resolution image with readable text or captions"},
            ],
            "recommendation": "Unable to verify this screenshot because no legible text was found. Please upload a clearer image.",
        }

    # 2. Extract Embedded URLs
    embedded_urls = extract_embedded_urls(ocr_text)
    primary_url = embedded_urls[0] if embedded_urls else None

    # 3. Analyze Embedded Website (if URL detected)
    website_res = None
    if primary_url:
        website_res = await analyze_website(primary_url)

    # 4. Decompose OCR Text into Atomic Claims
    claims_list = await extract_claims(ocr_text)

    # 5. Verify Claims against Independent Sources
    evidence_res = await verify_claims_and_retrieve_evidence(claims_list, ocr_text)

    # 6. Fuse Claim Evidence + Website Security Assessment
    verdict = evidence_res["verdict"]
    confidence = evidence_res["confidence"]
    risk_score = evidence_res["risk_score"]
    reasons = list(evidence_res["reasons"])
    sources = list(evidence_res["sources"])

    # Prepend OCR extraction confirmation
    ocr_preview = ocr_text.replace("\n", " ").strip()[:100]
    reasons.insert(0, {
        "type": "support",
        "text": f"OCR extracted {len(ocr_text)} characters from screenshot: \"{ocr_preview}...\"",
    })

    # If an embedded URL was found, synthesize website risks
    if website_res:
        sources.append({
            "name": f"Embedded Website Scanner ({website_res['domain']})",
            "type": "security-engine",
            "url": primary_url,
            "reliability": 0.92,
        })

        if website_res["risk_level"] in ("HIGH", "CRITICAL"):
            verdict = "LIKELY_FALSE"
            risk_score = max(risk_score, website_res["risk_score"], 85.0)
            confidence = max(confidence, 90.0)
            reasons.insert(1, {
                "type": "contradiction",
                "text": f"CRITICAL: Embedded link '{website_res['domain']}' flagged as {website_res['risk_level']} RISK ({website_res['risk_score']}/100)",
            })
            for sig in website_res.get("signals", [])[:2]:
                reasons.append({"type": "contradiction", "text": f"Link Risk: {sig}"})
        else:
            reasons.insert(1, {
                "type": "support" if website_res["https"] else "warning",
                "text": f"Embedded link '{website_res['domain']}' inspected ({website_res['risk_level']} Risk)",
            })

    # Recommendation synthesis
    if verdict == "LIKELY_FALSE":
        recommendation = "DO NOT CLICK embedded links or forward this screenshot. The claims and/or links contained in this image are fraudulent or debunked."
    elif verdict == "SUSPICIOUS":
        recommendation = "Exercise high caution. This screenshot contains unverified claims or suspicious website links. Avoid entering personal credentials."
    elif verdict == "UNVERIFIED":
        recommendation = "🟡 UNVERIFIED: The claims extracted from this screenshot could not be confirmed by authoritative sources. Treat with caution."
    else:
        recommendation = "The factual claims extracted from this screenshot are corroborated by independent reporting."

    return {
        "verdict": verdict,
        "confidence": confidence,
        "risk_score": risk_score,
        "evidence_coverage": evidence_res.get("evidence_coverage", 75.0),
        "ocr_text": ocr_text,
        "embedded_url": primary_url,
        "website_details": website_res,
        "claims": evidence_res["claims"],
        "sources": sources,
        "reasons": reasons,
        "recommendation": recommendation,
    }
