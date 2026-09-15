"""Automated tests for Website & URL Analyzer (Phase 5).

Verifies:
1. SSRF prevention and URL validation (localhost, loopback, private ranges, cloud metadata).
2. Domain and TLD heuristics (high-trust vs suspicious TLDs, keyword matching).
3. Multi-signal risk calculation and verdict assignment.
4. End-to-end analyze_website async execution.
"""

import pytest
import asyncio
from app.analyzers.website_analyzer import (
    validate_url_security,
    extract_domain_features,
    calculate_website_risk,
    analyze_website,
    is_private_ip,
)


def test_private_ip_detection():
    """Verify detection of RFC 1918 private, loopback, and reserved IP ranges."""
    assert is_private_ip("127.0.0.1") is True
    assert is_private_ip("127.0.0.5") is True
    assert is_private_ip("::1") is True
    assert is_private_ip("10.0.0.1") is True
    assert is_private_ip("192.168.1.1") is True
    assert is_private_ip("172.16.0.1") is True
    assert is_private_ip("169.254.169.254") is True  # AWS/Cloud metadata
    assert is_private_ip("0.0.0.0") is True

    # Public IPs
    assert is_private_ip("8.8.8.8") is False
    assert is_private_ip("1.1.1.1") is False


def test_ssrf_prevention():
    """Ensure SSRF attack targets are blocked immediately."""
    # Localhost
    safe, err, _ = validate_url_security("http://localhost:8000")
    assert safe is False
    assert "localhost" in err.lower() or "security" in err.lower()

    # 127.0.0.1
    safe, err, _ = validate_url_security("http://127.0.0.1:5000")
    assert safe is False

    # Private network
    safe, err, _ = validate_url_security("http://192.168.0.1/admin")
    assert safe is False

    # Cloud metadata endpoint
    safe, err, _ = validate_url_security("http://169.254.169.254/latest/meta-data")
    assert safe is False

    # Unsupported protocol
    safe, err, _ = validate_url_security("ftp://example.com/file")
    assert safe is False
    assert "scheme" in err.lower()

    # Valid public domain
    safe, err, norm_url = validate_url_security("https://python.org")
    assert safe is True
    assert norm_url == "https://python.org"


def test_domain_feature_extraction():
    """Test structural analysis of domains."""
    # Legitimate high-trust
    feat = extract_domain_features("https://pib.gov.in/PressRelease.aspx")
    assert feat["is_https"] is True
    assert feat["is_high_trust_tld"] is True
    assert feat["is_high_risk_tld"] is False

    # Suspicious domain with high risk TLD and keywords
    feat_phish = extract_domain_features("http://sbi-login-verify.top/auth")
    assert feat_phish["is_https"] is False
    assert feat_phish["is_high_risk_tld"] is True
    assert "sbi-" in feat_phish["suspicious_keywords"]
    assert feat_phish["hyphen_count"] >= 2


def test_risk_scoring_high_trust():
    """Ensure institutional / high-trust domains receive low risk scores and positive verdicts."""
    feat = extract_domain_features("https://wikipedia.org")
    page_data = {
        "success": True,
        "title": "Wikipedia, the free encyclopedia",
        "transparency_pages": ["about", "privacy", "terms"],
        "emails": ["info@wikimedia.org"],
        "has_phone": False,
        "has_password_field": False,
        "scam_patterns": [],
    }

    result = calculate_website_risk(feat, page_data)
    assert result["verdict"] == "LIKELY_TRUE"
    assert result["risk_level"] == "LOW"
    assert result["risk_score"] <= 25.0
    assert result["confidence"] >= 90.0


def test_risk_scoring_phishing_signals():
    """Ensure phishing indicators dramatically escalate risk score."""
    feat = {
        "hostname": "secure-sbi-login.top",
        "root_domain": "sbi-login.top",
        "tld": ".top",
        "is_https": False,
        "is_ip_host": False,
        "is_high_trust_tld": False,
        "is_high_trust_domain": False,
        "is_high_risk_tld": True,
        "suspicious_keywords": ["sbi-"],
        "hyphen_count": 2,
        "subdomain_count": 1,
    }
    page_data = {
        "success": True,
        "title": "Urgent Bank Verification",
        "transparency_pages": [],
        "emails": [],
        "has_phone": False,
        "has_password_field": True,  # Password on unencrypted HTTP!
        "scam_patterns": ["Urgent account verification demand"],
    }

    result = calculate_website_risk(feat, page_data)
    assert result["verdict"] == "LIKELY_FALSE"
    assert result["risk_level"] == "CRITICAL"
    assert result["risk_score"] >= 75.0


@pytest.mark.asyncio
async def test_analyze_website_ssrf_blocking():
    """Verify that analyze_website safely intercepts SSRF attempts asynchronously."""
    result = await analyze_website("http://127.0.0.1:8000/secret")
    assert result["verdict"] == "LIKELY_FALSE"
    assert result["risk_level"] == "CRITICAL"
    assert "SSRF" in result["signals"][0] or "Security" in result["signals"][0]
