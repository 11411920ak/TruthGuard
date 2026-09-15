"""Unit tests for Evidence Retrieval & Cross-Source Scoring Engine (Phase 7)."""

import pytest
from app.analyzers.evidence_engine import (
    calculate_source_reliability,
    detect_evidence_stance,
    verify_claims_and_retrieve_evidence,
)


def test_source_reliability_hierarchy():
    """Verify source weightings: official > fact-checker > major news > established > general > social."""
    gov_rel, gov_type, _ = calculate_source_reliability("pib.gov.in")
    assert gov_rel >= 0.95
    assert gov_type == "official"

    fc_rel, fc_type, _ = calculate_source_reliability("boomlive.in")
    assert fc_rel >= 0.90
    assert fc_type == "fact-checker"

    news_rel, news_type, _ = calculate_source_reliability("reuters.com")
    assert news_rel >= 0.85
    assert news_type == "news"

    gen_rel, gen_type, _ = calculate_source_reliability("random-example-blog.org")
    assert gen_rel <= 0.50
    assert gen_type == "general"

    soc_rel, soc_type, _ = calculate_source_reliability("twitter.com")
    assert soc_rel <= 0.25
    assert soc_type == "social"


def test_stance_detection_contradiction():
    """Verify stance detection recognizes debunking and contradiction keywords."""
    text = "PIB Fact Check clarified this is completely fake and debunked the viral message."
    stance, score = detect_evidence_stance(text)

    assert stance == "contradiction"
    assert score < 0.0


def test_stance_detection_support():
    """Verify stance detection recognizes official approvals and launch confirmations."""
    text = "The Cabinet officially approved the project and confirmed eligible beneficiaries."
    stance, score = detect_evidence_stance(text)

    assert stance == "support"
    assert score > 0.0


@pytest.mark.asyncio
async def test_known_fake_scheme_contradiction():
    """Verify known misinformation tropes yield LIKELY_FALSE with authoritative refutations."""
    claims = [
        {"claim_text": "Government announces free laptop to all students", "claim_type": "government announcement"}
    ]
    result = await verify_claims_and_retrieve_evidence(claims, "Government announces free laptop to all students")

    assert result["verdict"] == "LIKELY_FALSE"
    assert result["risk_score"] >= 80.0
    assert result["confidence"] >= 85.0
    assert any(s["type"] == "official" for s in result["sources"])
    assert any(r["type"] == "contradiction" for r in result["reasons"])


@pytest.mark.asyncio
async def test_unverified_decision_system():
    """Verify obscure, unconfirmed claims trigger UNVERIFIED rather than an unbacked FALSE."""
    claims = [
        {"claim_text": "A rare blue frog was discovered under a car in Pune yesterday", "claim_type": "general claim"}
    ]
    result = await verify_claims_and_retrieve_evidence(claims, "A rare blue frog was discovered under a car in Pune yesterday")

    assert result["verdict"] == "UNVERIFIED"
    assert result["confidence"] <= 60.0
    assert "UNVERIFIED" in result["recommendation"]
