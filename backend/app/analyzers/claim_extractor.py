"""Claim Extraction & Semantic Decomposition Engine for TruthGuard.

Decomposes raw text, news articles, and social media posts into:
1. Atomic, verifiable propositions / assertions.
2. Named entities & quantitative metrics (money, authorities, dates, schemes).
3. Claim taxonomy & categorization.
4. Filters out subjective opinions, rhetorical noise, and un-verifiable text.
5. Hybrid architecture: Deterministic rule-based NLP with optional LLM reasoning upgrade.
"""

import json
import re
from typing import Optional
from app.config import get_settings


# ── Entity Patterns ──

CURRENCY_PATTERN = re.compile(
    r"(?:₹|rs\.?|inr|\$|€|£)\s*\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:lakh|crore|thousand|k|m|b|million|billion))?|"
    r"\b\d+(?:,\d+)*(?:\s*(?:lakh|crore|thousand|million|billion))\s*(?:rupees|dollars|inr)\b",
    re.IGNORECASE,
)

AUTHORITY_PATTERN = re.compile(
    r"\b(government|govt|central\s+government|state\s+government|ministry\s+of\s+[a-z\s]+|"
    r"pmo|prime\s+minister|rbi|reserve\s+bank|sebi|isro|nasa|who|un|united\s+nations|"
    r"supreme\s+court|high\s+court|police|ugc|cbse|aicte|income\s+tax\s+department|"
    r"election\s+commission|drdo|niti\s+aayog)\b",
    re.IGNORECASE,
)

BENEFICIARY_PATTERN = re.compile(
    r"\b(college\s+students?|university\s+students?|students?|senior\s+citizens?|elderly|"
    r"farmers?|women|girl\s+child|youth|graduates?|unemployed\s+youth|citizens?|"
    r"taxpayers?|job\s+seekers?|pensioners?)\b",
    re.IGNORECASE,
)

SCHEME_PATTERN = re.compile(
    r"\b([a-z0-9\-]+(?:\s+[a-z0-9\-]+)?\s+(?:scheme|yojana|scholarship|grant|subsidy|portal|mission|fellowship|programme|program))\b",
    re.IGNORECASE,
)

DATE_DEADLINE_PATTERN = re.compile(
    r"\b(tomorrow|today|yesterday|next\s+week|deadline|applications?\s+open|starting\s+from|"
    r"(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:,\s*\d{4})?|"
    r"\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+\d{4})?|"
    r"\b\d{4}\b)\b",
    re.IGNORECASE,
)


# ── Noise & Rhetoric Patterns ──

OPINION_PREFIXES = [
    "i think", "i believe", "in my opinion", "personally", "i feel", "it seems to me",
    "just my thoughts", "what a great", "omg", "wow", "hello everyone", "please subscribe",
    "share this with everyone", "forwarded as received"
]

NON_CLAIM_PATTERNS = [
    r"^\s*(?:hello|hi|hey|good\s+morning|good\s+evening)\b",
    r"\?\s*$",  # Pure questions
    r"^\s*(?:click\s+here|follow\s+us|subscribe|share\s+now)\b",
]


# ── Entity Extraction ──

def extract_entities_from_text(text: str) -> list[str]:
    """Extract named entities, monetary values, institutions, and schemes from text."""
    entities = []

    # Currencies
    for match in CURRENCY_PATTERN.finditer(text):
        val = match.group(0).strip()
        if val and val not in entities:
            entities.append(val)

    # Authorities
    for match in AUTHORITY_PATTERN.finditer(text):
        val = match.group(0).strip().title()
        if val and val not in entities:
            entities.append(val)

    # Schemes
    for match in SCHEME_PATTERN.finditer(text):
        val = match.group(0).strip().title()
        if val and val not in entities:
            entities.append(val)

    # Beneficiaries
    for match in BENEFICIARY_PATTERN.finditer(text):
        val = match.group(0).strip().title()
        if val and val not in entities:
            entities.append(val)

    # Dates
    for match in DATE_DEADLINE_PATTERN.finditer(text):
        val = match.group(0).strip()
        if len(val) >= 3 and val not in entities and not val.isdigit():
            entities.append(val.capitalize())

    return entities[:8]  # Limit to 8 most relevant


# ── Taxonomy Classification ──

def classify_claim_type(claim_text: str, entities: list[str]) -> str:
    """Classify the claim into a standardized taxonomy category."""
    text_lower = claim_text.lower()
    entities_str = " ".join(entities).lower()

    if any(w in text_lower or w in entities_str for w in ["scholarship", "college", "student", "university", "exam", "cbse", "ugc", "degree"]):
        return "education & scholarship"
    elif any(w in text_lower or w in entities_str for w in ["scheme", "yojana", "announces", "government", "govt", "ministry", "policy", "cabinet", "pm"]):
        return "government announcement"
    elif any(w in text_lower or w in entities_str for w in ["₹", "$", "money", "rupees", "subsidy", "bank", "rbi", "loan", "free cash", "account", "pension"]):
        return "financial promise"
    elif any(w in text_lower or w in entities_str for w in ["vaccine", "cure", "covid", "cancer", "hospital", "doctor", "health", "who", "disease"]):
        return "health & medical"
    elif any(w in text_lower or w in entities_str for w in ["nasa", "isro", "space", "discovery", "ai", "robot", "satellite", "mars"]):
        return "science & technology"
    elif any(w in text_lower or w in entities_str for w in ["police", "arrest", "scam", "fraud", "court", "crime", "illegal", "ban"]):
        return "law & public safety"
    else:
        return "general claim"


# ── Atomic Claim Decomposition ──

def is_verifiable_claim(sentence: str) -> bool:
    """Determine if a sentence contains a verifiable assertion rather than pure rhetoric or a question."""
    cleaned = sentence.strip()
    if len(cleaned) < 10:
        return False

    # Filter questions
    if cleaned.endswith("?"):
        return False

    # Filter opinion prefixes
    cleaned_lower = cleaned.lower()
    for prefix in OPINION_PREFIXES:
        if cleaned_lower.startswith(prefix):
            return False

    # Filter noise patterns
    for pat in NON_CLAIM_PATTERNS:
        if re.search(pat, cleaned, re.IGNORECASE):
            return False

    return True


def split_into_candidate_sentences(text: str) -> list[str]:
    """
    Split text into candidate sentences while preserving numbers and abbreviations.
    E.g. preserves '₹50,000', 'Rs. 500', 'Dr.', 'Govt.', etc.
    """
    # Protect common abbreviations and numbers with decimals
    normalized = re.sub(r"\b(Govt|Dr|Prof|Mr|Mrs|Ms|vs|e\.g|i\.e)\.\s*", r"\1<DOT> ", text, flags=re.IGNORECASE)
    normalized = re.sub(r"(\d+)\.(\d+)", r"\1<DECIMAL>\2", normalized)

    # Split by sentence terminators or line breaks
    raw_sentences = re.split(r"(?<=[.!?\n])\s+", normalized)

    results = []
    for s in raw_sentences:
        clean = s.replace("<DOT>", ".").replace("<DECIMAL>", ".").strip()
        # Clean extra quotes or bullet prefixes
        clean = re.sub(r"^[\s\-\*•\d\.\)]+", "", clean).strip()
        if clean:
            results.append(clean)

    return results


def decompose_text_into_claims(text: str) -> list[dict]:
    """
    Rule-based semantic claim decomposition.
    Decomposes multi-sentence paragraphs into individual atomic claims.
    """
    sentences = split_into_candidate_sentences(text)
    claims = []

    for sentence in sentences:
        if not is_verifiable_claim(sentence):
            continue

        # Extract entities
        entities = extract_entities_from_text(sentence)

        # Categorize
        claim_type = classify_claim_type(sentence, entities)

        # Determine initial estimate/verdict for the claim
        # E.g. Check for typical scam keywords like "free laptop to every student"
        verdict = "UNVERIFIED"
        confidence = 50.0

        sentence_lower = sentence.lower()
        if any(w in sentence_lower for w in ["free laptop to every", "100% free money", "guaranteed 20 lpa", "click here to claim"]):
            verdict = "LIKELY_FALSE"
            confidence = 88.0
        elif any(w in sentence_lower for w in ["announced", "launched", "scholarship", "subsidy"]):
            verdict = "UNVERIFIED"
            confidence = 65.0

        claims.append({
            "claim_text": sentence,
            "claim_type": claim_type,
            "entities": entities,
            "verdict": verdict,
            "confidence": confidence,
        })

    # If no atomic claims could be extracted, return input as a single general claim
    if not claims:
        entities = extract_entities_from_text(text)
        claims.append({
            "claim_text": text.strip()[:300],
            "claim_type": classify_claim_type(text, entities),
            "entities": entities,
            "verdict": "UNVERIFIED",
            "confidence": 45.0,
        })

    return claims


# ── Optional LLM Extraction Engine ──

async def extract_claims_with_llm(text: str, api_key: str) -> Optional[list[dict]]:
    """
    Optionally use LLM API (e.g. Gemini) for deep semantic decomposition if API key is provided.
    Falls back to rule-based engine on any error or timeout.
    """
    try:
        import httpx

        prompt = (
            "You are TruthGuard's Claim Extraction Engine. Decompose the following text into distinct, atomic, verifiable factual claims.\n"
            "For each claim, provide:\n"
            "- 'claim_text': A concise, factual assertion\n"
            "- 'claim_type': Category ('government announcement', 'education & scholarship', 'financial promise', 'health & medical', 'general claim')\n"
            "- 'entities': List of key named entities (organizations, amounts, people, dates)\n"
            "- 'verdict': 'UNVERIFIED'\n"
            "- 'confidence': 60.0\n\n"
            f"Input Text:\n\"{text}\"\n\n"
            "Respond ONLY with a JSON array of claim objects."
        )

        # Example endpoint for Gemini REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(raw_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    return parsed
    except Exception:
        # Fallback to local deterministic extractor
        pass

    return None


# ── Main Entrypoint ──

async def extract_claims(text: str) -> list[dict]:
    """
    Main entry point for claim extraction.
    Attempts LLM extraction if an AI API key is configured; otherwise uses deterministic rule-based NLP.
    """
    settings = get_settings()

    # If AI API key is configured, attempt LLM extraction
    if settings.ai_api_key:
        llm_claims = await extract_claims_with_llm(text, settings.ai_api_key)
        if llm_claims:
            return llm_claims

    # Deterministic local NLP extractor (100% local, fast, reliable)
    return decompose_text_into_claims(text)
