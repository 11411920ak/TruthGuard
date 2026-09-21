"""Social Media Content & Viral Disinformation Analyzer for TruthGuard.

Performs:
1. Platform identification (Twitter/X, WhatsApp, Telegram, Instagram, Reddit, Facebook).
2. Handle and hashtag extraction (@username, #hashtags).
3. Account impersonation & bot detection heuristics (spoofed government/banking handles).
4. Viral urgency & emotional manipulation scoring (chain forwards, artificial panic, fake authority citing).
5. Embedded link scanning (shorteners, scam redirects).
6. Dual-engine cross-source evidence verification.
"""

import re
from typing import Optional

from app.analyzers.claim_extractor import extract_claims
from app.analyzers.evidence_engine import verify_claims_and_retrieve_evidence
from app.analyzers.website_analyzer import analyze_website
from app.analyzers.image_analyzer import extract_embedded_urls


# ── Platform Detection Patterns ──

PLATFORM_PATTERNS = [
    (r"(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/", "Twitter / X"),
    (r"(?:https?://)?(?:www\.)?t\.me/", "Telegram"),
    (r"(?:https?://)?(?:www\.)?instagram\.com/", "Instagram"),
    (r"(?:https?://)?(?:www\.)?(?:facebook\.com|fb\.watch)/", "Facebook"),
    (r"(?:https?://)?(?:www\.)?reddit\.com/", "Reddit"),
    (r"(?:https?://)?(?:www\.)?(?:wa\.me|chat\.whatsapp\.com)/", "WhatsApp"),
]

WHATSAPP_FORWARD_MARKERS = [
    "forwarded many times",
    "forwarded as received",
    "as received",
    "whatsapp forward",
    "share with 10",
    "share with 5",
    "forward to 10",
    "forward to all",
    "share in all groups",
    "send to 10 people",
    "don't break the chain",
]

# ── Impersonation Target Watchlist ──

OFFICIAL_AUTHORITIES = [
    "pib", "pibfactcheck", "rbi", "reservebank", "pmo", "pm_modi",
    "sbi", "statebank", "who", "cdc", "unicef", "nasa", "isro",
    "railways", "irctc", "uidai", "aadhaar", "incometax", "cbse",
]

SUSPICIOUS_HANDLE_SUFFIXES = [
    "_official", "_real", "_bonus", "_reward", "_support", "_helpdesk",
    "_update", "_gov", "_portal", "_service", "_claim", "24x7",
]

# ── Viral Urgency & Manipulation Patterns ──

URGENCY_KEYWORDS = [
    "urgent", "alert", "breaking", "warning", "before midnight", "immediately",
    "account suspended", "act now", "last chance", "don't ignore", "hurry up",
]

CHAIN_FORWARD_PATTERNS = [
    r"share (?:with|to) \d+",
    r"forward (?:to|with) \d+",
    r"send (?:to|with) \d+",
    r"don'?t break (?:the|this) chain",
    r"within \d+ (?:hours|minutes)",
    r"before midnight",
]

UNVERIFIED_AUTHORITY_PATTERNS = [
    r"unesco declared",
    r"nasa confirmed",
    r"who declared",
    r"supreme court ordered",
    r"army announced",
    r"satellite captured",
    r"secret order",
]


def detect_platform(text: str) -> str:
    """Identify social media platform from text markers or URL domains."""
    for pattern, platform_name in PLATFORM_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return platform_name

    text_lower = text.lower()
    for marker in WHATSAPP_FORWARD_MARKERS:
        if marker in text_lower:
            return "WhatsApp Forward"

    if "@" in text and ("rt " in text_lower or "#" in text):
        return "Twitter / X"

    return "Social Media Post"


def extract_social_entities(text: str) -> dict:
    """Extract handles, hashtags, and platforms from social text."""
    handles = re.findall(r"@([a-zA-Z0-9_]{1,30})\b", text)
    hashtags = re.findall(r"#([a-zA-Z0-9_]{1,50})\b", text)
    clean_handles = list(dict.fromkeys(handles))
    clean_hashtags = list(dict.fromkeys(hashtags))
    return {
        "handles": clean_handles,
        "hashtags": clean_hashtags,
    }


def analyze_impersonation(handles: list[str]) -> dict:
    """Detect potential spoofing of official governmental/banking handles."""
    flags = []
    max_risk = "NONE"
    risk_score = 0.0

    for handle in handles:
        h_lower = handle.lower()
        # Check against target authorities
        matched_authority = None
        for auth in OFFICIAL_AUTHORITIES:
            if auth in h_lower:
                matched_authority = auth
                break

        if matched_authority:
            # Check for impersonation markers
            has_suffix = any(suf in h_lower for suf in SUSPICIOUS_HANDLE_SUFFIXES)
            has_trailing_digits = bool(re.search(r"\d{2,}$", h_lower))
            has_double_underscore = "__" in h_lower

            if has_suffix or has_trailing_digits or has_double_underscore:
                risk_score = max(risk_score, 85.0)
                max_risk = "HIGH"
                flags.append(
                    f"Handle '@{handle}' exhibits spoofing patterns mimicking official entity '{matched_authority.upper()}'"
                )
            else:
                risk_score = max(risk_score, 25.0)
                max_risk = "LOW"
                flags.append(f"Handle '@{handle}' references known entity '{matched_authority.upper()}'")

        # Bot-like handle patterns (excessive digits or hex sequences)
        elif re.search(r"^[a-zA-Z]+[0-9]{5,}$", handle):
            risk_score = max(risk_score, 65.0)
            if max_risk in ("NONE", "LOW"):
                max_risk = "MEDIUM"
            flags.append(f"Handle '@{handle}' matches auto-generated bot naming pattern")

    return {
        "impersonation_risk": max_risk,
        "risk_score": risk_score,
        "flags": flags,
    }


def analyze_virality_and_manipulation(text: str) -> dict:
    """Score viral urgency, chain-letter propagation, and emotional manipulation."""
    text_lower = text.lower()
    signals = []
    score = 0.0

    # 1. Forward Markers
    is_forwarded = any(marker in text_lower for marker in WHATSAPP_FORWARD_MARKERS)
    if is_forwarded:
        score += 25.0
        signals.append("Contains unverified viral forward markers ('Forwarded as received')")

    # 2. Urgency keywords
    urgency_count = sum(1 for kw in URGENCY_KEYWORDS if re.search(r"\b" + kw + r"\b", text_lower))
    if urgency_count >= 2:
        score += 30.0
        signals.append(f"High artificial urgency detected ({urgency_count} urgency triggers)")
    elif urgency_count == 1:
        score += 15.0
        signals.append("Subtle urgency triggers detected")

    # 3. Chain forward / coercive demands
    for pat in CHAIN_FORWARD_PATTERNS:
        if re.search(pat, text_lower):
            score += 35.0
            signals.append("Coercive chain forwarding demand detected ('Share with X contacts')")
            break

    # 4. Viral disinfo tropes
    for pat in VIRAL_DISINFO_TROPES:
        if re.search(pat, text_lower):
            score += 15
            clean_trope = pat.replace(r"\b", "")
            signals.append(f"Common viral disinfo trope detected: '{clean_trope}'")
            break

    normalized_score = min(100.0, score)
    level = "HIGH" if normalized_score >= 60 else ("MEDIUM" if normalized_score >= 30 else "LOW")

    return {
        "manipulation_level": level,
        "manipulation_score": normalized_score,
        "signals": signals,
    }


# ── End-to-End Social Post Verification ──

async def analyze_social_post(text: str) -> dict:
    """
    Main orchestrator for Social Media & Viral Content Verification:
    1. Detects platform and extracts handles/hashtags.
    2. Runs account impersonation heuristics.
    3. Analyzes virality and emotional manipulation signals.
    4. Extracts embedded links and inspects domain risk.
    5. Extracts factual claims and verifies cross-source evidence.
    6. Combines signals into authoritative verdict and risk score.
    """
    # 1. Metadata and platform extraction
    platform = detect_platform(text)
    entities = extract_social_entities(text)

    # 2. Impersonation & bot analysis
    impersonation = analyze_impersonation(entities["handles"])

    # 3. Viral manipulation analysis
    virality = analyze_virality_and_manipulation(text)

    # 4. Embedded URL scanning
    embedded_urls = extract_embedded_urls(text)
    primary_url = embedded_urls[0] if embedded_urls else None
    website_res = None
    if primary_url:
        website_res = await analyze_website(primary_url)

    # 5. Claim decomposition & Evidence Retrieval
    claims_list = await extract_claims(text)
    evidence_res = await verify_claims_and_retrieve_evidence(claims_list, text)

    # 6. Risk & Verdict Synthesis
    verdict = evidence_res["verdict"]
    confidence = evidence_res["confidence"]
    risk_score = evidence_res["risk_score"]
    reasons = list(evidence_res["reasons"])
    sources = list(evidence_res["sources"])

    # Prepend social platform & virality context
    reasons.insert(0, {
        "type": "warning" if virality["manipulation_level"] in ("HIGH", "MEDIUM") else "support",
        "text": f"Platform: {platform} — Virality/Manipulation Risk: {virality['manipulation_level']} ({virality['manipulation_score']}/100)",
    })

    # Add virality signals
    for sig in virality["signals"]:
        reasons.append({"type": "contradiction", "text": f"Social Signal: {sig}"})

    # Add impersonation flags
    if impersonation["impersonation_risk"] in ("HIGH", "MEDIUM"):
        reasons.append({
            "type": "contradiction",
            "text": f"Account Security: Impersonation risk is {impersonation['impersonation_risk']}",
        })
        for flag in impersonation["flags"]:
            reasons.append({"type": "contradiction", "text": flag})
        risk_score = max(risk_score, impersonation["risk_score"])
        if impersonation["impersonation_risk"] == "HIGH":
            verdict = "LIKELY_FALSE"
            confidence = max(confidence, 88.0)

    # Factor in embedded website security
    if website_res:
        sources.append({
            "name": f"Embedded Link Scanner ({website_res['domain']})",
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
                "text": f"Scam Link Detected: Embedded URL '{website_res['domain']}' flagged as {website_res['risk_level']} Risk ({website_res['risk_score']}/100)",
            })

    # Adjust recommendation for social context
    if verdict == "LIKELY_FALSE":
        recommendation = "🛑 DO NOT FORWARD OR CLICK. This post exhibits high manipulation, unverified claims, or spoofed account indicators."
    elif verdict == "SUSPICIOUS":
        recommendation = "⚠️ SUSPICIOUS. High viral urgency or unverified claims detected. Avoid forwarding to groups or clicking links."
    elif verdict == "UNVERIFIED":
        recommendation = "🟡 UNVERIFIED: No authoritative corroboration found for this social post. Treat as unconfirmed rumor."
    else:
        recommendation = "✅ The factual claims in this post are supported by credible independent reporting."

    social_details = {
        "platform": platform,
        "handles": entities["handles"],
        "hashtags": entities["hashtags"],
        "impersonation_risk": impersonation["impersonation_risk"],
        "impersonation_flags": impersonation["flags"],
        "manipulation_level": virality["manipulation_level"],
        "manipulation_score": virality["manipulation_score"],
        "manipulation_signals": virality["signals"],
        "embedded_url": primary_url,
    }

    return {
        "verdict": verdict,
        "confidence": confidence,
        "risk_score": risk_score,
        "evidence_coverage": evidence_res.get("evidence_coverage", 70.0),
        "social_details": social_details,
        "website_details": website_res,
        "claims": evidence_res["claims"],
        "sources": sources,
        "reasons": reasons,
        "recommendation": recommendation,
    }
