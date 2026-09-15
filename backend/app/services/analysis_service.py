"""Analysis service — orchestrates the verification pipeline.

Currently returns mock results. Will be replaced with real AI logic
in later phases (claim extraction, evidence retrieval, scoring).
"""

from datetime import datetime, timezone

from app.models.database import Analysis, Claim, Source, Evidence, Result, get_session_factory
from app.config import get_settings
from app.analyzers.website_analyzer import analyze_website


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
    - If input_type == 'url' or looks like a URL: runs real website_analyzer
    - Otherwise: runs text/claim verification pipeline
    """
    settings = get_settings()
    session_factory = get_session_factory(settings.database_url)

    is_url = input_type == "url" or input_content.strip().startswith(("http://", "https://", "www."))

    if is_url:
        # Run real website security and reputation analysis
        result_data = await analyze_website(input_content)
    else:
        # Select appropriate mock for text claims (prior to Phase 6+ LLM/search integration)
        mock = _select_mock(input_content)
        result_data = {
            "verdict": mock["verdict"],
            "confidence": mock["confidence"],
            "risk_score": mock["risk_score"],
            "evidence_coverage": mock["evidence_coverage"],
            "claims": [
                {
                    "claim_text": c["claim_text"] or input_content,
                    "claim_type": c["claim_type"],
                    "verdict": c["verdict"],
                    "confidence": c["confidence"],
                }
                for c in mock["claims"]
            ],
            "sources": mock["sources"],
            "reasons": mock["reasons"],
            "signals": [r["text"] for r in mock["reasons"]],
            "recommendation": mock["recommendation"],
        }

    async with session_factory() as session:
        analysis = await session.get(Analysis, analysis_id)
        if not analysis:
            return {"error": "Analysis not found"}

        analysis.status = "completed"
        analysis.verdict = result_data["verdict"]
        analysis.confidence = result_data["confidence"]
        analysis.risk_score = result_data["risk_score"]
        analysis.evidence_coverage = result_data["evidence_coverage"]

        # Create sources first so we have source IDs if needed
        sources_created = []
        for src_data in result_data.get("sources", []):
            source = Source(
                analysis_id=analysis_id,
                title=src_data.get("name"),
                source_type=src_data.get("type"),
                reliability_score=src_data.get("reliability", 0.8),
            )
            session.add(source)
            sources_created.append(source)

        await session.flush()

        # Create claims and attach evidence (signals)
        primary_source_id = sources_created[0].id if sources_created else None
        for claim_data in result_data.get("claims", []):
            claim = Claim(
                analysis_id=analysis_id,
                claim_text=claim_data["claim_text"],
                claim_type=claim_data.get("claim_type", "claim"),
                verdict=claim_data.get("verdict", result_data["verdict"]),
                confidence=claim_data.get("confidence", result_data["confidence"]),
            )
            session.add(claim)
            await session.flush()

            # Store signals/evidence linked to this claim
            for signal_text in result_data.get("signals", []):
                evidence_type = "warning"
                if "✓" in signal_text or "Verified" in signal_text or "active" in signal_text or "found" in signal_text.lower():
                    evidence_type = "support"
                elif "CRITICAL" in signal_text or "Violation" in signal_text or "Insecure" in signal_text:
                    evidence_type = "contradiction"

                evidence = Evidence(
                    claim_id=claim.id,
                    source_id=primary_source_id,
                    evidence_text=signal_text,
                    evidence_type=evidence_type,
                    support_score=1.0 if evidence_type == "support" else -1.0 if evidence_type == "contradiction" else 0.0,
                )
                session.add(evidence)

        # Format reasons string for Result.explanation
        reasons_list = result_data.get("reasons", [])
        explanation_parts = []
        for r in reasons_list:
            if isinstance(r, dict):
                rtype = r.get("type", "warning")
                rtext = r.get("text", "")
                explanation_parts.append(f"[{rtype}] {rtext}")
            else:
                explanation_parts.append(str(r))

        result = Result(
            analysis_id=analysis_id,
            verdict=result_data["verdict"],
            confidence=result_data["confidence"],
            explanation="; ".join(explanation_parts),
            recommendation=result_data.get("recommendation", ""),
        )
        session.add(result)

        await session.commit()

    return {
        "id": analysis_id,
        "verdict": result_data["verdict"],
        "confidence": result_data["confidence"],
    }
