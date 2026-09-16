"""
Tests for NewsAPI integration in TruthGuard.
"""

import pytest
from app.services.newsapi import search_news, get_newsapi_key
from app.analyzers.evidence_engine import query_news_api


def test_newsapi_key_configured():
    """Verify that NEWS_API_KEY is properly loaded from environment."""
    key = get_newsapi_key()
    assert key != ""
    assert len(key) >= 10


def test_service_newsapi_search():
    """Verify search_news service function returns live articles."""
    res = search_news("artificial intelligence", page_size=3)
    assert isinstance(res, dict)
    assert res.get("status") == "ok"
    assert "articles" in res
    assert len(res["articles"]) > 0


@pytest.mark.asyncio
async def test_evidence_engine_query_news_api():
    """Verify query_news_api converts articles into evidence records with reliability & stance."""
    key = get_newsapi_key()
    results = await query_news_api("technology innovation", api_key=key)
    assert isinstance(results, list)
    assert len(results) > 0

    first = results[0]
    assert "title" in first
    assert "url" in first
    assert "publisher" in first
    assert "reliability" in first
    assert "stance" in first
    assert first["source_type"] in ("news", "established", "general", "official", "unknown")
