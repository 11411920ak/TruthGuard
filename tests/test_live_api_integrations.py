"""
Verification test confirming all 4 external APIs (Google Fact Check, Serper, Tavily, Gemini)
operate seamlessly when invoked through TruthGuard's evidence engine.
"""

import pytest
from app.analyzers.evidence_engine import (
    query_google_fact_check,
    query_serper_search,
    query_tavily_search,
    query_gemini_reasoning,
    verify_claims_and_retrieve_evidence,
)
from app.config import get_settings


@pytest.mark.asyncio
async def test_live_google_fact_check_api():
    """Verify live Google Fact Check Tools API returns verified claims."""
    settings = get_settings()
    assert settings.google_fact_check_api_key, "GOOGLE_FACT_CHECK_API_KEY must be set"
    results = await query_google_fact_check("free laptop scheme", settings.google_fact_check_api_key)
    assert len(results) > 0, "Expected at least 1 result from Google Fact Check API"
    assert results[0]["source_type"] == "fact-checker"
    assert "reliability" in results[0]


@pytest.mark.asyncio
async def test_live_serper_search_api():
    """Verify live Serper Google Search API returns search results."""
    settings = get_settings()
    assert settings.search_api_key, "SEARCH_API_KEY must be set"
    results = await query_serper_search("free laptop scheme", settings.search_api_key)
    assert len(results) > 0, "Expected at least 1 result from Serper Search API"
    assert results[0]["url"].startswith("http")


@pytest.mark.asyncio
async def test_live_tavily_search_api():
    """Verify live Tavily Search API returns context results."""
    settings = get_settings()
    assert settings.tavily_api_key, "TAVILY_API_KEY must be set"
    results = await query_tavily_search("free laptop scheme", settings.tavily_api_key)
    assert len(results) > 0, "Expected at least 1 result from Tavily Search API"
    assert len(results[0]["snippet"]) > 0


@pytest.mark.asyncio
async def test_live_gemini_ai_reasoning():
    """Verify live Google Gemini 3.6 Flash returns semantic analysis."""
    settings = get_settings()
    assert settings.ai_api_key, "AI_API_KEY must be set"
    insight = await query_gemini_reasoning(
        "Government gives free 5G recharge for 3 months to all SIM cards",
        settings.ai_api_key,
    )
    assert insight is not None, "Gemini must return an analysis string"
    assert len(insight) > 10
    assert "false" in insight.lower() or "scam" in insight.lower()


@pytest.mark.asyncio
async def test_live_end_to_end_verification_pipeline():
    """Verify the full pipeline orchestrates all 4 APIs into a unified verdict."""
    extracted_claims = [
        {"claim_text": "Free 5G recharge for 3 months announced by telecom ministry for all users", "claim_type": "promotion claim", "entities": []}
    ]
    result = await verify_claims_and_retrieve_evidence(
        extracted_claims,
        "Free 5G recharge for 3 months announced by telecom ministry for all users",
    )
    assert result["verdict"] in ("LIKELY_FALSE", "SUSPICIOUS")
    assert len(result["sources"]) > 0
    assert len(result["reasons"]) > 0
