"""Analysis service — orchestrates the verification pipeline.

Currently returns mock results. Will be replaced with real AI logic
in later phases (claim extraction, evidence retrieval, scoring).
"""

from datetime import datetime, timezone

from app.models.database import Analysis, Claim, Source, Evidence, Result, get_session_factory
from app.config import get_settings


# ── Mock analysis data ──
# These simulate what the real AI pipeline will produce

MOCK_VERDICTS = {
    "government": {
        "verdict": "LIKELY_FALSE",
        "confidence": 91,
        "risk_score": 87,
        "evidence_coverage": 84,
        "claims": [
            {"claim_text": "", "claim_type": "government announcement", "verdict": "LIKELY_FALSE", "confidence": 91},
        ],
        "reasons": [
            {"type": "contradiction", "text": "Official government education portal does not list this scheme"},
            {"type": "contradiction", "text": "Multiple reputable news sources report no such announcement"},
            {"type": "warning", "text": "Original source could not be independently verified"},
            {"type": "warning", "text": "Similar claims have been flagged as misinformation by fact-checkers"},
        ],
        "sources": [
            {"name": "Government Education Portal", "type": "official", "reliability": 0.95},
            {"name": "Reuters India", "type": "news", "reliability": 0.88},
            {"name": "BOOM Fact Check", "type": "fact-checker", "reliability": 0.90},
            {"name": "The Hindu", "type": "news", "reliability": 0.85},
            {"name": "PIB Fact Check", "type": "official", "reliability": 0.95},
        ],
        "recommendation": "Do not share this claim as confirmed. No official government source has announced this scheme. This appears to be misinformation circulating on social media.",
    },
    "default": {
        "verdict": "UNVERIFIED",
        "confidence": 45,
        "risk_score": 50,
        "evidence_coverage": 30,
        "claims": [
            {"claim_text": "", "claim_type": "general claim", "verdict": "UNVERIFIED", "confidence": 45},
        ],
        "reasons": [
            {"type": "warning", "text": "Limited reliable sources found for this claim"},
            {"type": "warning", "text": "No official confirmation or denial could be located"},
            {"type": "warning", "text": "Claim could not be independently verified with available evidence"},
        ],
        "sources": [
            {"name": "Web Search Results", "type": "search", "reliability": 0.50},
            {"name": "Social Media", "type": "social", "reliability": 0.30},
        ],
        "recommendation": "There is insufficient reliable evidence to confirm or reject this claim. Exercise caution before sharing.",
    },
}


def _select_mock(content: str) -> dict:
    """Select a mock response based on content keywords."""
    content_lower = content.lower()

    # Check for government-related keywords
    gov_keywords = ["government", "sarkar", "sarkari", "ministry", "scheme", "scholarship",
                     "free laptop", "free money", "subsidy", "yojana", "modi"]
    for kw in gov_keywords:
        if kw in content_lower:
            return MOCK_VERDICTS["government"]

    return MOCK_VERDICTS["default"]


async def run_analysis(analysis_id: str, input_type: str, input_content: str) -> dict:
    """
    Run the verification pipeline on the given content.

    Currently returns mock results. In later phases, this will:
    1. Extract claims (LLM)
    2. Search for evidence (search APIs)
    3. Analyze source reliability
    4. Calculate confidence scores
    5. Produce verdict
    """
    settings = get_settings()
    session_factory = get_session_factory(settings.database_url)

    # Select appropriate mock
    mock = _select_mock(input_content)

    async with session_factory() as session:
        # Update analysis status
        analysis = await session.get(Analysis, analysis_id)
        if not analysis:
            return {"error": "Analysis not found"}

        analysis.status = "completed"
        analysis.verdict = mock["verdict"]
        analysis.confidence = mock["confidence"]
        analysis.risk_score = mock["risk_score"]
        analysis.evidence_coverage = mock["evidence_coverage"]

        # Create claims
        for claim_data in mock["claims"]:
            claim = Claim(
                analysis_id=analysis_id,
                claim_text=claim_data["claim_text"] or input_content,
                claim_type=claim_data["claim_type"],
                verdict=claim_data["verdict"],
                confidence=claim_data["confidence"],
            )
            session.add(claim)

        # Create sources
        for src_data in mock["sources"]:
            source = Source(
                analysis_id=analysis_id,
                title=src_data["name"],
                source_type=src_data["type"],
                reliability_score=src_data["reliability"],
            )
            session.add(source)

        # Create result
        result = Result(
            analysis_id=analysis_id,
            verdict=mock["verdict"],
            confidence=mock["confidence"],
            explanation="; ".join(r["text"] for r in mock["reasons"]),
            recommendation=mock["recommendation"],
        )
        session.add(result)

        await session.commit()

    return {
        "id": analysis_id,
        "verdict": mock["verdict"],
        "confidence": mock["confidence"],
    }
