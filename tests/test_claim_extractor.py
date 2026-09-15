"""Unit tests for Claim Extraction & Decomposition Engine (Phase 6)."""

import pytest
from app.analyzers.claim_extractor import (
    extract_entities_from_text,
    classify_claim_type,
    split_into_candidate_sentences,
    decompose_text_into_claims,
    extract_claims,
    is_verifiable_claim,
)


def test_entity_extraction_monetary_and_authorities():
    """Verify extraction of financial metrics, institutions, and schemes."""
    text = "Government announces ₹50,000 scholarship for every college student under PM-Kisan."
    entities = extract_entities_from_text(text)

    assert any("₹50,000" in e for e in entities)
    assert any("Government" in e for e in entities)
    assert any("Student" in e for e in entities)
    assert any("Scholarship" in e or "Scheme" in e or "Pm-Kisan" in e for e in entities)


def test_claim_type_classification():
    """Verify taxonomy categorization for different types of assertions."""
    assert classify_claim_type("Government announces new subsidy for farmers", ["Government", "Farmers"]) in (
        "government announcement", "financial promise"
    )
    assert classify_claim_type("Students will receive ₹50,000 scholarship grant", ["₹50,000", "Scholarship"]) == "education & scholarship"
    assert classify_claim_type("New vaccine cures cancer clinical trial begins", ["Vaccine", "Cancer"]) == "health & medical"
    assert classify_claim_type("NASA discovers water ice deposits on Mars", ["NASA", "Mars"]) == "science & technology"


def test_multi_claim_decomposition():
    """Verify compound text is decomposed into distinct atomic propositions."""
    post = (
        "Government launches Scheme X. "
        "Students will receive ₹50,000. "
        "Applications open tomorrow."
    )

    claims = decompose_text_into_claims(post)
    assert len(claims) == 3

    assert "Scheme X" in claims[0]["claim_text"] or "Government" in claims[0]["claim_text"]
    assert "₹50,000" in claims[1]["claim_text"]
    assert "Applications" in claims[2]["claim_text"] or "tomorrow" in claims[2]["claim_text"].lower()

    # Verify each claim has its own entities
    assert any("₹50,000" in ent for ent in claims[1]["entities"])


def test_opinion_and_noise_filtering():
    """Verify rhetorical noise and opinions are filtered out while preserving factual assertions."""
    text = "I believe this is amazing! The Ministry of Education released the official cutoff list yesterday."
    claims = decompose_text_into_claims(text)

    assert len(claims) == 1
    assert "Ministry of Education" in claims[0]["claim_text"]
    assert not any("I believe" in c["claim_text"] for c in claims)


@pytest.mark.asyncio
async def test_async_extract_claims_pipeline():
    """Verify full asynchronous extract_claims function."""
    content = "Government announces ₹50,000 scholarship for every college student."
    extracted = await extract_claims(content)

    assert len(extracted) >= 1
    assert extracted[0]["claim_type"] in ("education & scholarship", "government announcement")
    assert any("₹50,000" in ent for ent in extracted[0]["entities"])
