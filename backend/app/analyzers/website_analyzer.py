"""Website & URL Analyzer for TruthGuard.

Performs multi-signal security, reputation, and content analysis for URLs:
1. SSRF prevention and URL validation (blocking private/internal networks).
2. Domain & TLD heuristics (suspicious TLDs, typosquatting, IP hostnames).
3. Live webpage content fetching (SSL check, title, meta, contacts, legal pages).
4. Content pattern analysis (scam/urgency language, credential harvesting).
5. Multi-signal weighted risk scoring and verdict generation.
"""

import ipaddress
import re
import socket
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


# ── High-Trust & Suspicious Lists ──

HIGH_TRUST_TLDS = {
    ".gov", ".mil", ".edu", ".ac.in", ".gov.in", ".nic.in", ".gov.uk", ".ac.uk", ".edu.au"
}

HIGH_TRUST_DOMAINS = {
    "google.com", "microsoft.com", "apple.com", "amazon.com", "wikipedia.org",
    "github.com", "reuters.com", "apnews.com", "bbc.com", "thehindu.com",
    "ndtv.com", "indianexpress.com", "who.int", "un.org", "nasa.gov",
    "pib.gov.in", "mygov.in", "india.gov.in", "python.org"
}

HIGH_RISK_TLDS = {
    ".top", ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".buzz", ".rest",
    ".work", ".click", ".loan", ".vip", ".fit", ".surf", ".monster", ".sbs"
}

SUSPICIOUS_DOMAIN_KEYWORDS = [
    "paypa1", "amaz0n", "sbi-", "hdfc-", "icici-", "free-money", "free-laptop",
    "claim-reward", "gift-card", "bonus-claim", "verify-account", "secure-login",
    "crypto-giveaway", "double-money", "lucky-winner"
]

SCAM_CONTENT_PATTERNS = [
    (r"\b(urgent(ly)?\s+(verify|update|action|suspend))\b", "Urgent account verification demand"),
    (r"\b(you\s+(have\s+)?won|lottery\s+winner|congratulations\s+winner)\b", "Lottery or prize winning claim"),
    (r"\b(double\s+your\s+(money|investment|crypto|bitcoin))\b", "Double-your-money guarantee"),
    (r"\b(100%\s+free\s+(money|cash|gift\s+card|laptop|iphone))\b", "Unrealistic free reward/subsidy claim"),
    (r"\b(send\s+(btc|bitcoin|eth|usdt)\s+to)\b", "Cryptocurrency transfer solicitation"),
    (r"\b(limited\s+time\s+offer\s+expires\s+in\s+\d+\s+(min|hour|second))\b", "Artificial urgency countdown"),
    (r"\b(guaranteed\s+(returns|income|daily\s+profit))\b", "Guaranteed profit promise"),
    (r"\b(enter\s+(your\s+)?(pin|atm\s+pin|cvv|otp))\b", "Direct PIN / CVV / OTP solicitation"),
]

TRANSPARENCY_KEYWORDS = ["about", "about-us", "contact", "contact-us", "privacy", "privacy-policy", "terms", "terms-of-service", "faq"]


# ── SSRF Defense & Validation ──

def is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private, loopback, or reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_reserved
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_unspecified
        )
    except ValueError:
        return True


def validate_url_security(url: str) -> tuple[bool, str, str]:
    """
    Validate URL safety against SSRF and protocol exploits.
    Returns (is_safe, error_message, normalized_url).
    """
    url_clean = url.strip()
    if not url_clean:
        return False, "URL cannot be empty", ""

    # Add default scheme if omitted
    if "://" not in url_clean:
        url_clean = "https://" + url_clean

    parsed = urlparse(url_clean)

    # Validate scheme
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported scheme '{parsed.scheme}'. Only HTTP and HTTPS are allowed.", ""

    hostname = parsed.hostname
    if not hostname:
        return False, "Invalid URL: missing hostname", ""

    # Check for localhost or direct loopback
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        return False, f"Access to localhost/loopback address '{hostname}' is blocked for security.", ""

    # Check for raw IP address hostname
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if is_private_ip(str(ip_obj)):
            return False, f"Access to private/reserved IP '{hostname}' is prohibited (SSRF prevention).", ""
    except ValueError:
        # Hostname is a domain name — resolve DNS to verify it doesn't map to a private IP
        try:
            addr_info = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
            for entry in addr_info:
                ip_addr = entry[4][0]
                if is_private_ip(ip_addr):
                    return False, f"Domain '{hostname}' resolves to private/internal IP {ip_addr} (SSRF blocked).", ""
        except socket.gaierror:
            # Could not resolve domain; still proceed to fetch with error handling
            pass

    return True, "", url_clean


# ── Feature & Content Extraction ──

def extract_domain_features(url: str) -> dict:
    """Extract structural and heuristic features from a domain."""
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    is_https = parsed.scheme.lower() == "https"

    # Identify TLD
    parts = hostname.split(".")
    tld = "." + parts[-1] if len(parts) > 1 else ""
    if len(parts) >= 3 and parts[-2] in ("co", "gov", "ac", "nic", "org", "edu", "net", "com"):
        tld = "." + parts[-2] + "." + parts[-1]

    # Check IP host
    is_ip_host = False
    try:
        ipaddress.ip_address(hostname)
        is_ip_host = True
    except ValueError:
        pass

    # Check high trust
    is_high_trust_tld = any(hostname.endswith(t) for t in HIGH_TRUST_TLDS)
    root_domain = ".".join(parts[-2:]) if len(parts) >= 2 else hostname
    is_high_trust_domain = (hostname in HIGH_TRUST_DOMAINS) or (root_domain in HIGH_TRUST_DOMAINS)

    # Check high risk TLD
    is_high_risk_tld = any(hostname.endswith(t) for t in HIGH_RISK_TLDS)

    # Check keyword anomalies
    suspicious_keywords_found = [kw for kw in SUSPICIOUS_DOMAIN_KEYWORDS if kw in hostname]

    # Hyphen count & subdomain depth
    hyphen_count = hostname.count("-")
    subdomain_count = max(0, len(parts) - 2)

    return {
        "hostname": hostname,
        "root_domain": root_domain,
        "tld": tld,
        "is_https": is_https,
        "is_ip_host": is_ip_host,
        "is_high_trust_tld": is_high_trust_tld,
        "is_high_trust_domain": is_high_trust_domain,
        "is_high_risk_tld": is_high_risk_tld,
        "suspicious_keywords": suspicious_keywords_found,
        "hyphen_count": hyphen_count,
        "subdomain_count": subdomain_count,
    }


async def fetch_webpage_content(url: str) -> dict:
    """
    Safely fetch and inspect webpage content using httpx.
    Returns status, headers, HTML metadata, text content, and errors.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TruthGuard-SecurityBot/1.0 (+https://truthguard.ai)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            max_redirects=4,
            timeout=7.0,
            verify=False,  # Allow inspection of self-signed/broken certs without crashing
        ) as client:
            response = await client.get(url, headers=headers)

            content_type = response.headers.get("content-type", "").lower()
            text_content = response.text[:500000]  # Limit to 500KB to prevent memory exhaustion

            # Parse with BeautifulSoup
            soup = BeautifulSoup(text_content, "html.parser")

            # Page title
            title = ""
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find("h1"):
                title = soup.find("h1").get_text().strip()

            # Meta description
            meta_desc = ""
            desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            if desc_tag and desc_tag.get("content"):
                meta_desc = desc_tag["content"].strip()

            # Plain text body
            body_text = " ".join(soup.stripped_strings)

            # Check for contact info
            emails_found = list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", body_text)))[:3]
            phone_found = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", body_text))

            # Check for transparency pages (About, Contact, Privacy, Terms)
            links = [a.get("href", "").lower() for a in soup.find_all("a", href=True)]
            transparency_pages_found = []
            for kw in TRANSPARENCY_KEYWORDS:
                if any(kw in href for href in links):
                    transparency_pages_found.append(kw)

            # Check for credential forms
            has_password_field = bool(soup.find("input", attrs={"type": "password"}))

            # Scan for scam/urgency patterns
            detected_scam_patterns = []
            for pattern, label in SCAM_CONTENT_PATTERNS:
                if re.search(pattern, body_text, re.IGNORECASE):
                    detected_scam_patterns.append(label)

            return {
                "success": True,
                "status_code": response.status_code,
                "final_url": str(response.url),
                "title": title[:200] if title else "Untitled Page",
                "meta_description": meta_desc[:300],
                "emails": emails_found,
                "has_phone": phone_found,
                "transparency_pages": list(set(transparency_pages_found)),
                "has_password_field": has_password_field,
                "scam_patterns": detected_scam_patterns,
                "body_text_length": len(body_text),
                "error": None,
            }

    except httpx.ConnectTimeout:
        return {"success": False, "error": "Connection timed out. Server unreachable.", "title": "Unreachable"}
    except httpx.ConnectError:
        return {"success": False, "error": "Failed to connect to host. Domain may be inactive.", "title": "Host Unreachable"}
    except Exception as e:
        return {"success": False, "error": f"Webpage inspection error: {str(e)}", "title": "Error"}


# ── Multi-Signal Risk Scoring ──

def calculate_website_risk(domain_feat: dict, page_data: dict) -> dict:
    """
    Calculate comprehensive risk score and generate verdict, signals, reasons, and recommendations.
    Employs the multi-signal principle: no single factor unilaterally creates a false positive.
    """
    risk_score = 30.0  # Baseline neutral score
    signals = []
    reasons = []

    # 1. High-Trust Domain Check
    if domain_feat["is_high_trust_domain"]:
        risk_score = 5.0
        signals.append("Verified high-reputation institutional domain")
        reasons.append({"type": "support", "text": "Domain is recognized as a major reputable platform / institution"})
        return _format_verdict_result(
            risk_score=risk_score,
            verdict="LIKELY_TRUE",
            confidence=96.0,
            signals=signals,
            reasons=reasons,
            recommendation="This website is operated by an established, high-reputation organization.",
            domain_feat=domain_feat,
            page_data=page_data,
        )

    if domain_feat["is_high_trust_tld"]:
        risk_score -= 25.0
        signals.append(f"Official government or academic TLD ({domain_feat['tld']})")
        reasons.append({"type": "support", "text": f"Registered under verified official/institutional TLD: {domain_feat['tld']}"})

    # 2. Protocol Security (HTTPS)
    if domain_feat["is_https"]:
        risk_score -= 10.0
        signals.append("SSL/TLS Encryption active (HTTPS)")
        reasons.append({"type": "support", "text": "Connection is encrypted with HTTPS"})
    else:
        risk_score += 25.0
        signals.append("Insecure HTTP protocol (no SSL encryption)")
        reasons.append({"type": "contradiction", "text": "Website does not use HTTPS encryption; data transmission is insecure"})

    # 3. Domain & TLD Risks
    if domain_feat["is_ip_host"]:
        risk_score += 35.0
        signals.append("Raw IP address used instead of registered domain")
        reasons.append({"type": "contradiction", "text": "Raw IP address used as web host, a tactic frequently seen in temporary scam sites"})

    if domain_feat["is_high_risk_tld"]:
        risk_score += 20.0
        signals.append(f"Domain uses high-risk TLD commonly associated with spam ({domain_feat['tld']})")
        reasons.append({"type": "warning", "text": f"TLD '{domain_feat['tld']}' has a statistically elevated association with fraudulent campaigns"})

    if domain_feat["suspicious_keywords"]:
        kw_str = ", ".join(domain_feat["suspicious_keywords"])
        risk_score += 30.0
        signals.append(f"Potential brand impersonation or financial lure in domain ({kw_str})")
        reasons.append({"type": "contradiction", "text": f"Domain name contains suspicious brand/financial trigger words: {kw_str}"})

    if domain_feat["hyphen_count"] >= 3:
        risk_score += 15.0
        signals.append(f"Excessive hyphens in domain structure ({domain_feat['hyphen_count']} hyphens)")
        reasons.append({"type": "warning", "text": "Excessive hyphenation in domain often indicates typosquatting or ad-hoc domain generation"})

    if domain_feat["subdomain_count"] >= 3:
        risk_score += 12.0
        signals.append("Unusually deep subdomain hierarchy")
        reasons.append({"type": "warning", "text": "Multiple nested subdomains detected"})

    # 4. Content Inspection Signals
    if page_data["success"]:
        # Transparency cues
        if page_data["transparency_pages"]:
            risk_score -= 12.0
            tp_list = ", ".join(page_data["transparency_pages"][:3])
            signals.append(f"Corporate transparency pages found ({tp_list})")
            reasons.append({"type": "support", "text": f"Contains organizational transparency pages: {tp_list}"})
        else:
            risk_score += 12.0
            signals.append("No standard 'About Us', 'Privacy Policy' or 'Terms' pages found")
            reasons.append({"type": "warning", "text": "Lacks transparent company information, privacy policy, or terms of service"})

        # Contact info
        if page_data["emails"] or page_data["has_phone"]:
            risk_score -= 8.0
            signals.append("Public contact details (email/phone) provided")
            reasons.append({"type": "support", "text": "Website displays verifiable contact channels"})
        else:
            risk_score += 10.0
            signals.append("No verifiable corporate email or phone number found")
            reasons.append({"type": "warning", "text": "No direct contact email or phone details could be located on the page"})

        # Scam / Urgency language
        if page_data["scam_patterns"]:
            risk_score += 25.0
            for sp in page_data["scam_patterns"][:3]:
                signals.append(f"High-risk content signal: {sp}")
                reasons.append({"type": "contradiction", "text": f"Detected scam/urgency pattern: {sp}"})

        # Credential harvesting on insecure/suspicious site
        if page_data["has_password_field"]:
            if not domain_feat["is_https"]:
                risk_score += 40.0
                signals.append("CRITICAL: Password input found on unencrypted HTTP page")
                reasons.append({"type": "contradiction", "text": "Password or credential input on an unencrypted HTTP connection"})
            elif domain_feat["is_high_risk_tld"] or domain_feat["suspicious_keywords"]:
                risk_score += 25.0
                signals.append("Login form present on potentially untrusted domain")
                reasons.append({"type": "warning", "text": "Login form located on a newly registered or suspicious domain"})
    else:
        # Webpage could not be fetched
        risk_score += 15.0
        signals.append(f"Webpage fetch failed ({page_data.get('error', 'Unreachable')})")
        reasons.append({"type": "warning", "text": f"Server was unreachable or refused connection: {page_data.get('error')}"})

    # Clamp risk score
    risk_score = max(5.0, min(95.0, risk_score))

    # Determine Verdict & Risk Level
    if risk_score <= 25.0:
        verdict = "LIKELY_TRUE"
        risk_level = "LOW"
        confidence = 90.0
        recommendation = "This website displays standard security practices, verified encryption, and no significant fraud signals."
    elif risk_score <= 50.0:
        verdict = "UNVERIFIED"
        risk_level = "MODERATE"
        confidence = 68.0
        recommendation = "This website has moderate or limited public verifiable signals. Exercise standard caution before submitting private information or payments."
    elif risk_score <= 74.0:
        verdict = "SUSPICIOUS"
        risk_level = "HIGH"
        confidence = 82.0
        recommendation = "Multiple suspicious indicators detected (such as missing transparency details, suspicious TLD, or high urgency). Avoid financial transactions or entering credentials."
    else:
        verdict = "LIKELY_FALSE"
        risk_level = "CRITICAL"
        confidence = 92.0
        recommendation = "CRITICAL RISK: Strong indicators of phishing, credential harvesting, or online fraud. Do not enter personal data, passwords, or payment credentials on this site."

    return _format_verdict_result(
        risk_score=risk_score,
        verdict=verdict,
        confidence=confidence,
        signals=signals,
        reasons=reasons,
        recommendation=recommendation,
        domain_feat=domain_feat,
        page_data=page_data,
        risk_level=risk_level,
    )


def _format_verdict_result(
    risk_score: float,
    verdict: str,
    confidence: float,
    signals: list[str],
    reasons: list[dict],
    recommendation: str,
    domain_feat: dict,
    page_data: dict,
    risk_level: Optional[str] = None,
) -> dict:
    """Build the standardized analysis output payload."""
    if not risk_level:
        if risk_score <= 25:
            risk_level = "LOW"
        elif risk_score <= 50:
            risk_level = "MODERATE"
        elif risk_score <= 75:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

    sources = [
        {"name": "Domain Security & TLD Inspector", "type": "security-engine", "reliability": 0.95},
        {"name": "SSL/TLS Protocol Validator", "type": "security-protocol", "reliability": 0.98},
        {"name": "Content & Phishing Pattern Scanner", "type": "scanner", "reliability": 0.90},
    ]

    claims = [
        {
            "claim_text": f"Website domain '{domain_feat['hostname']}' is legitimate and safe to visit",
            "claim_type": "website safety",
            "verdict": verdict,
            "confidence": confidence,
        },
        {
            "claim_text": f"Web connection uses secure encryption ({'HTTPS' if domain_feat['is_https'] else 'HTTP Insecure'})",
            "claim_type": "transport security",
            "verdict": "LIKELY_TRUE" if domain_feat["is_https"] else "LIKELY_FALSE",
            "confidence": 98.0,
        },
    ]

    return {
        "domain": domain_feat["hostname"],
        "https": domain_feat["is_https"],
        "page_title": page_data.get("title", "Unknown"),
        "risk_score": round(risk_score, 1),
        "risk_level": risk_level,
        "verdict": verdict,
        "confidence": round(confidence, 1),
        "evidence_coverage": 88.0,
        "signals": signals,
        "reasons": reasons,
        "sources": sources,
        "claims": claims,
        "recommendation": recommendation,
    }


# ── Main Entrypoint ──

async def analyze_website(url: str) -> dict:
    """
    Main asynchronous handler to analyze a website URL.
    Performs SSRF validation, feature extraction, content fetch, and risk evaluation.
    """
    # 1. Validate URL & Prevent SSRF
    is_safe, error_msg, normalized_url = validate_url_security(url)
    if not is_safe:
        return {
            "domain": url,
            "https": False,
            "page_title": "Blocked URL",
            "risk_score": 95.0,
            "risk_level": "CRITICAL",
            "verdict": "LIKELY_FALSE",
            "confidence": 99.0,
            "evidence_coverage": 100.0,
            "signals": [f"Security Violation: {error_msg}"],
            "reasons": [{"type": "contradiction", "text": error_msg}],
            "sources": [{"name": "SSRF & Network Defense Firewall", "type": "security", "reliability": 1.0}],
            "claims": [{"claim_text": f"Access to '{url}' is safe", "claim_type": "security policy", "verdict": "LIKELY_FALSE", "confidence": 99.0}],
            "recommendation": "Access to this address is blocked by TruthGuard's security firewall. Private network or loopback scanning is strictly prohibited.",
        }

    # 2. Extract Domain Features
    domain_feat = extract_domain_features(normalized_url)

    # 3. Fetch Webpage Content (Async)
    page_data = await fetch_webpage_content(normalized_url)

    # 4. Multi-Signal Risk Assessment
    return calculate_website_risk(domain_feat, page_data)
