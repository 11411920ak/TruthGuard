"""Unit tests for Social Media Verification Engine (Phase 9)."""

import pytest
from app.analyzers.social_analyzer import (
    detect_platform,
    extract_social_entities,
    analyze_impersonation,
    analyze_virality_and_manipulation,
    analyze_social_post,
)


def test_detect_platform():
    assert detect_platform("Check out this tweet: https://twitter.com/elonmusk/status/123") == "Twitter / X"
    assert detect_platform("Join our channel: https://t.me/cryptoleaks") == "Telegram"
    assert detect_platform("Forwarded many times: Important alert for all citizens") == "WhatsApp Forward"
    assert detect_platform("Watch this reel https://instagram.com/reel/xyz") == "Instagram"
    assert detect_platform("Regular random statement with no social traces") == "Social Media Post"


def test_extract_social_entities():
    post = "Attention: @PIBFactCheck and @PMOIndia declared scheme. Tagging #FakeScheme #FactCheck2026."
    res = extract_social_entities(post)
    assert "PIBFactCheck" in res["handles"]
    assert "PMOIndia" in res["handles"]
    assert "FakeScheme" in res["hashtags"]
    assert "FactCheck2026" in res["hashtags"]


def test_analyze_impersonation_detection():
    # High risk spoofing pattern
    spoofed = analyze_impersonation(["PIBFactCheck_official_1", "RBI_support247"])
    assert spoofed["impersonation_risk"] == "HIGH"
    assert len(spoofed["flags"]) >= 1

    # Normal authority reference
    legit = analyze_impersonation(["PIBFactCheck"])
    assert legit["impersonation_risk"] == "LOW"

    # Bot handle
    bot = analyze_impersonation(["user98234871"])
    assert bot["impersonation_risk"] == "MEDIUM"


def test_analyze_virality_and_manipulation():
    viral_text = (
        "Forwarded as received: URGENT WARNING! Don't ignore! "
        "Share to 10 friends immediately before midnight or account blocked!"
    )
    res = analyze_virality_and_manipulation(viral_text)
    assert res["manipulation_level"] == "HIGH"
    assert res["manipulation_score"] >= 60
    assert len(res["signals"]) >= 2


@pytest.mark.asyncio
async def test_analyze_social_post_end_to_end():
    post = (
        "Forwarded many times: @PIBFactCheck_bonus announces free ₹50,000 allowance. "
        "Share to 5 groups to activate now at http://claim-funds.xyz"
    )
    res = await analyze_social_post(post)
    assert res["verdict"] in ("LIKELY_FALSE", "SUSPICIOUS")
    assert res["risk_score"] >= 70.0
    assert "social_details" in res
    assert res["social_details"]["platform"] == "WhatsApp Forward"
    assert res["social_details"]["impersonation_risk"] == "HIGH"
    assert res["social_details"]["manipulation_level"] in ("HIGH", "MEDIUM")
