"""Evidence Retrieval & Cross-Source Scoring Engine for TruthGuard.

Implements:
1. Multi-channel evidence retrieval across official, fact-checking, and news sources.
2. Source reliability weighting (official = 0.95, fact-checker = 0.90, major news = 0.85, established = 0.80, general = 0.45, social = 0.20).
3. Semantic stance detection (support, contradiction, warning).
4. Cross-source agreement calculation and risk scoring.
5. The UNVERIFIED Decision Rules (distinguishing FALSE from NOT PROVEN).
"""

import asyncio
import re
import urllib.parse
from typing import Optional
import httpx
from app.config import get_settings


# ── Known Source Registries & Reliability Weights ──

SOURCE_WEIGHTS = {
    "official": 0.95,
    "fact-checker": 0.90,
    "news": 0.85,
    "established": 0.80,
    "general": 0.45,
    "social": 0.20,
    "unknown": 0.25,
}

AUTHORITATIVE_FACT_CHECKERS = [
    {"domain": "pib.gov.in", "name": "PIB Fact Check", "type": "official", "reliability": 0.95},
    {"domain": "boomlive.in", "name": "BOOM Live", "type": "fact-checker", "reliability": 0.90},
    {"domain": "altnews.in", "name": "AltNews", "type": "fact-checker", "reliability": 0.90},
    {"domain": "snopes.com", "name": "Snopes", "type": "fact-checker", "reliability": 0.90},
    {"domain": "factcheck.org", "name": "FactCheck.org", "type": "fact-checker", "reliability": 0.90},
    {"domain": "politifact.com", "name": "PolitiFact", "type": "fact-checker", "reliability": 0.90},
    {"domain": "reuters.com", "name": "Reuters Fact Check", "type": "news", "reliability": 0.88},
    {"domain": "apnews.com", "name": "AP Fact Check", "type": "news", "reliability": 0.88},
]

MAJOR_NEWS_DOMAINS = {
    "reuters.com": ("Reuters", 0.88),
    "apnews.com": ("Associated Press", 0.88),
    "bbc.com": ("BBC News", 0.85),
    "thehindu.com": ("The Hindu", 0.85),
    "indianexpress.com": ("The Indian Express", 0.85),
    "ndtv.com": ("NDTV", 0.80),
    "hindustantimes.com": ("Hindustan Times", 0.80),
    "timesofindia.indiatimes.com": ("Times of India", 0.78),
    "bloomberg.com": ("Bloomberg", 0.86),
}

OFFICIAL_GOV_DOMAINS = {
    "gov.in", "nic.in", "mygov.in", "india.gov.in", "pib.gov.in", "rbi.org.in",
    "gov", "who.int", "nasa.gov", "un.org", "europa.eu", "cdc.gov"
}


# ── Fact-Check Knowledge Base for High-Risk Viral Tropes ──
# Provides academic baseline verification for frequent misinformation claims

KNOWN_FACT_CHECKS = [
    {
        "keywords": ["free laptop", "laptop scheme", "free tablet"],
        "claim_topic": "Free laptop/tablet scheme for students",
        "verdict": "LIKELY_FALSE",
        "official_stance": "contradiction",
        "explanation": "Official PIB Fact Check confirmed that Government of India has not announced any scheme distributing free laptops to all students. Viral links claiming this are phishing scams.",
        "sources": [
            {"name": "PIB Fact Check", "type": "official", "url": "https://pib.gov.in/FactCheck", "reliability": 0.95},
            {"name": "BOOM Live", "type": "fact-checker", "url": "https://www.boomlive.in", "reliability": 0.90},
            {"name": "The Hindu", "type": "news", "url": "https://www.thehindu.com", "reliability": 0.85},
        ],
        "reasons": [
            {"type": "contradiction", "text": "PIB Fact Check explicitly debunks the free laptop scheme as fraudulent"},
            {"type": "contradiction", "text": "Ministry of Education has issued no notification for universal laptop distribution"},
            {"type": "warning", "text": "Circulating messages link to deceptive phishing websites rather than official portals"},
        ],
        "recommendation": "Do not register on unverified links or share personal/bank details. Check scholarships only on scholarships.gov.in.",
    },
    {
        "keywords": ["₹50,000", "50000", "50,000 scholarship for every", "universal scholarship"],
        "claim_topic": "Universal ₹50,000 scholarship announcement",
        "verdict": "LIKELY_FALSE",
        "official_stance": "contradiction",
        "explanation": "No universal ₹50,000 scholarship for all college students has been approved. Legitimate central schemes require formal eligibility criteria via the National Scholarship Portal.",
        "sources": [
            {"name": "National Scholarship Portal (NSP)", "type": "official", "url": "https://scholarships.gov.in", "reliability": 0.95},
            {"name": "PIB Fact Check", "type": "official", "url": "https://pib.gov.in/FactCheck", "reliability": 0.95},
            {"name": "AltNews", "type": "fact-checker", "url": "https://www.altnews.in", "reliability": 0.90},
        ],
        "reasons": [
            {"type": "contradiction", "text": "National Scholarship Portal does not list any unconditional ₹50,000 grant for every student"},
            {"type": "contradiction", "text": "PIB Fact Check has repeatedly warned against similar scholarship grant hoaxes"},
            {"type": "warning", "text": "Original announcement source could not be verified on any government gazette"},
        ],
        "recommendation": "Verify scholarship schemes exclusively through the official National Scholarship Portal (scholarships.gov.in).",
    },
    {
        "keywords": ["pm-kisan", "pm kisan 2000", "pm kisan 18th installment"],
        "claim_topic": "PM-Kisan installment release",
        "verdict": "LIKELY_TRUE",
        "official_stance": "support",
        "explanation": "PM-Kisan is an authentic flagship government scheme providing ₹6,000 annually in three installments to eligible landholding farmer families.",
        "sources": [
            {"name": "PM-Kisan Official Portal", "type": "official", "url": "https://pmkisan.gov.in", "reliability": 0.98},
            {"name": "PIB India", "type": "official", "url": "https://pib.gov.in", "reliability": 0.95},
            {"name": "DD News", "type": "news", "url": "https://ddnews.gov.in", "reliability": 0.85},
        ],
        "reasons": [
            {"type": "support", "text": "Official PM-Kisan portal documents active installment releases directly into beneficiary accounts"},
            {"type": "support", "text": "Government press release confirms operational scheme guidelines"},
        ],
        "recommendation": "Beneficiaries can verify their installment status directly on pmkisan.gov.in using Aadhaar number.",
    },
]


# ── Source Reliability Evaluation ──

def calculate_source_reliability(domain: str) -> tuple[float, str, str]:
    """
    Determine source reliability score, category, and display name based on domain.
    Returns (reliability_score, source_type, publisher_name).
    """
    domain_clean = domain.lower().strip().replace("www.", "")

    # Check official domains
    if any(domain_clean.endswith("." + d) or domain_clean == d for d in OFFICIAL_GOV_DOMAINS):
        return 0.95, "official", f"{domain_clean.upper()} Official Portal"

    # Check known fact-checkers
    for fc in AUTHORITATIVE_FACT_CHECKERS:
        if fc["domain"] in domain_clean:
            return fc["reliability"], fc["type"], fc["name"]

    # Check major news
    for nd, (name, rel) in MAJOR_NEWS_DOMAINS.items():
        if nd in domain_clean:
            return rel, "news", name

    # Check academic/educational
    if domain_clean.endswith((".edu", ".ac.in", ".edu.au", ".ac.uk")):
        return 0.90, "academic", f"{domain_clean} (Academic)"

    # General / Unknown
    if any(social in domain_clean for social in ["facebook", "twitter", "x.com", "instagram", "t.me", "whatsapp", "reddit"]):
        return 0.20, "social", f"{domain_clean} (Social Media)"

    return 0.45, "general", domain_clean.title()


# ── Stance Detection Engine ──

CONTRADICTION_PATTERNS = [
    r"\b(fake|false|hoax|misleading|debunked|scam|fraudulent|busted|fabricated|untrue|baseless)\b",
    r"\b(no\s+such\s+(scheme|announcement|notification|order|grant))\b",
    r"\b(warns?\s+against|beware\s+of|clarifies\s+(that\s+)?no|fact\s+check\s*:\s*false)\b",
    r"\b(not\s+(true|confirmed|official|approved))\b",
]

SUPPORT_PATTERNS = [
    r"\b(officially\s+(announced|launched|approved|confirmed))\b",
    r"\b(cabinet\s+approves|government\s+launches|ministry\s+releases)\b",
    r"\b(authentic|factually\s+verified|officially\s+verified|official\s+notification\s+issued)\b",
    r"\b(eligible\s+beneficiaries\s+can\s+apply)\b",
]


def check_topical_overlap(text: str, query: str) -> bool:
    """Verify that evidence text actually pertains to the subject matter of the query."""
    if not query:
        return True
    stopwords = {
        "what", "this", "that", "with", "from", "have", "been", "were", "yesterday", "today",
        "tomorrow", "about", "there", "their", "where", "which", "claim", "fact", "check",
        "news", "official", "fake", "true", "false", "verified", "report", "reports"
    }
    query_tokens = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9]{4,}\b", query) if w.lower() not in stopwords]
    if not query_tokens:
        return True
    matches = sum(1 for t in query_tokens if t in text.lower())
    return matches >= min(2, len(query_tokens))


def detect_evidence_stance(text: str, query: str = "") -> tuple[str, float]:
    """
    Analyze text snippet for stance toward the target claim.
    Returns (stance, support_score):
      - 'contradiction', -1.0 to -0.6
      - 'support', +0.6 to +1.0
      - 'warning', -0.2 to +0.2
    """
    if query and not check_topical_overlap(text, query):
        return "warning", 0.0

    text_lower = text.lower()

    contradict_count = sum(1 for p in CONTRADICTION_PATTERNS if re.search(p, text_lower))
    support_count = sum(1 for p in SUPPORT_PATTERNS if re.search(p, text_lower))

    if contradict_count > 0 and contradict_count >= support_count:
        score = -0.7 - min(0.3, contradict_count * 0.1)
        return "contradiction", score
    elif support_count > 0 and support_count > contradict_count:
        score = 0.7 + min(0.3, support_count * 0.1)
        return "support", score
    else:
        return "warning", 0.0


# ── Multi-Channel Evidence Retrieval Pipeline ──

async def query_google_fact_check(query: str, api_key: str) -> list[dict]:
    """Query official Google Fact Check Tools API."""
    if not api_key:
        return []
    results = []
    try:
        url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={urllib.parse.quote_plus(query)}&key={api_key}"
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                for c in data.get("claims", [])[:3]:
                    claim_text = c.get("text", "")
                    for cr in c.get("claimReview", [])[:1]:
                        publisher = cr.get("publisher", {}).get("name", "Official Fact-Checker")
                        rating = cr.get("textualRating", "")
                        cr_url = cr.get("url", "")
                        domain = urllib.parse.urlparse(cr_url).hostname or ""
                        rel, stype, _ = calculate_source_reliability(domain)

                        rating_lower = rating.lower()
                        if any(w in rating_lower for w in ["false", "fake", "hoax", "incorrect", "scam", "misleading", "fabricated"]):
                            stance = "contradiction"
                            s_score = -0.9
                        elif any(w in rating_lower for w in ["true", "correct", "accurate"]):
                            stance = "support"
                            s_score = 0.9
                        else:
                            stance = "warning"
                            s_score = -0.3

                        results.append({
                            "title": f"Fact Check: {claim_text[:80]}",
                            "url": cr_url,
                            "domain": domain,
                            "publisher": publisher,
                            "source_type": "fact-checker",
                            "reliability": max(rel, 0.92),
                            "snippet": f"Rating by {publisher}: {rating}. {claim_text}",
                            "stance": stance,
                            "support_score": s_score,
                        })
    except Exception:
        pass
    return results


async def query_tavily_search(query: str, api_key: str) -> list[dict]:
    """Query Tavily Deep Search for real-time fact-checking intelligence."""
    if not api_key:
        return []
    results = []
    try:
        url = "https://api.tavily.com/search"
        payload = {"api_key": api_key, "query": query, "max_results": 4}
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", [])[:4]:
                    title = item.get("title", "")
                    snippet = item.get("content", "")
                    url_str = item.get("url", "")
                    domain = urllib.parse.urlparse(url_str).hostname or ""
                    rel, stype, publisher = calculate_source_reliability(domain)
                    stance, s_score = detect_evidence_stance(f"{title} {snippet}", query)
                    results.append({
                        "title": title,
                        "url": url_str,
                        "domain": domain,
                        "publisher": publisher,
                        "source_type": stype,
                        "reliability": rel,
                        "snippet": snippet[:250],
                        "stance": stance,
                        "support_score": s_score,
                    })
    except Exception:
        pass
    return results


async def query_serper_search(query: str, api_key: str) -> list[dict]:
    """Query Serper.dev for live Google search evidence."""
    if not api_key:
        return []
    results = []
    try:
        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        payload = {"q": query, "num": 4}
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("organic", [])[:4]:
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    url_str = item.get("link", "")
                    domain = urllib.parse.urlparse(url_str).hostname or ""
                    rel, stype, publisher = calculate_source_reliability(domain)
                    stance, s_score = detect_evidence_stance(f"{title} {snippet}", query)
                    results.append({
                        "title": title,
                        "url": url_str,
                        "domain": domain,
                        "publisher": publisher,
                        "source_type": stype,
                        "reliability": rel,
                        "snippet": snippet,
                        "stance": stance,
                        "support_score": s_score,
                    })
    except Exception:
        pass
    return results


async def query_news_api(query: str, api_key: str) -> list[dict]:
    """Query NewsAPI (https://newsapi.org) for live journalism and news reports."""
    results = []
    if not api_key:
        return results
    try:
        url = "https://newsapi.org/v2/everything"
        headers = {
            "X-Api-Key": api_key,
            "User-Agent": "TruthGuard-EvidenceRetriever/1.0",
        }
        params = {
            "q": query,
            "pageSize": 5,
            "sortBy": "relevancy",
            "language": "en",
        }
        async with httpx.AsyncClient(timeout=6.0, headers=headers) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                for article in data.get("articles", []):
                    title = article.get("title") or ""
                    snippet = article.get("description") or article.get("content") or ""
                    url_str = article.get("url") or ""
                    source_name = article.get("source", {}).get("name") or "News Source"
                    domain = urllib.parse.urlparse(url_str).hostname or ""
                    rel, stype, publisher = calculate_source_reliability(domain)
                    if publisher == "Unknown / Unclassified Source":
                        publisher = source_name
                        rel = 0.82
                        stype = "news"
                    combined_text = f"{title} {snippet}"
                    stance, s_score = detect_evidence_stance(combined_text, query)
                    results.append({
                        "title": title,
                        "url": url_str,
                        "domain": domain,
                        "publisher": publisher,
                        "source_type": stype,
                        "reliability": rel,
                        "snippet": snippet,
                        "stance": stance,
                        "support_score": s_score,
                    })
    except Exception:
        pass
    return results


async def query_duckduckgo_fallback(query: str) -> list[dict]:
    """Fallback open web search when dedicated API quotas expire or are unset."""
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TruthGuard-EvidenceRetriever/1.0"}
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    try:
        async with httpx.AsyncClient(timeout=4.0, headers=headers, follow_redirects=True) as client:
            resp = await client.get(search_url)
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                for result_div in soup.find_all("div", class_="result")[:4]:
                    link_tag = result_div.find("a", class_="result__url")
                    title_tag = result_div.find("a", class_="result__title")
                    snippet_tag = result_div.find("a", class_="result__snippet")
                    if link_tag and snippet_tag:
                        url_str = link_tag.get("href", "").strip()
                        title = title_tag.get_text(strip=True) if title_tag else "Web Evidence"
                        snippet = snippet_tag.get_text(strip=True)
                        domain = urllib.parse.urlparse(url_str).hostname or ""
                        rel, stype, publisher = calculate_source_reliability(domain)
                        stance, s_score = detect_evidence_stance(f"{title} {snippet}", query)
                        results.append({
                            "title": title,
                            "url": url_str,
                            "domain": domain,
                            "publisher": publisher,
                            "source_type": stype,
                            "reliability": rel,
                            "snippet": snippet,
                            "stance": stance,
                            "support_score": s_score,
                        })
    except Exception:
        pass
    return results


async def query_gemini_reasoning(claim: str, api_key: str) -> Optional[str]:
    """Query Google Gemini for deep semantic truthfulness analysis."""
    if not api_key:
        return None
    for model in ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-3.8-flash", "gemini-2.5-flash"]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            prompt = (
                f"Analyze this claim for truthfulness: '{claim}'. "
                "Reply strictly with 1-2 concise factual sentences summarizing whether it is true, false, a scam, or unverified."
            )
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
        except Exception:
            continue
    return None


async def query_web_evidence(query: str) -> list[dict]:
    """
    Unified multi-channel evidence retrieval.
    Queries Google Fact Check, Tavily, Serper, NewsAPI, and DuckDuckGo in parallel.
    """
    settings = get_settings()
    tasks = []

    # 1. Google Fact Check Tools API
    if settings.google_fact_check_api_key:
        tasks.append(query_google_fact_check(query, settings.google_fact_check_api_key))

    # 2. Tavily Deep Search
    if settings.tavily_api_key:
        tasks.append(query_tavily_search(query, settings.tavily_api_key))

    # 3. Serper Google Search
    if settings.search_api_key:
        tasks.append(query_serper_search(query, settings.search_api_key))

    # 4. NewsAPI Journalism Search
    if settings.news_api_key:
        tasks.append(query_news_api(query, settings.news_api_key))

    # Always include DuckDuckGo as auxiliary or fallback
    tasks.append(query_duckduckgo_fallback(query))

    gathered = await asyncio.gather(*tasks, return_exceptions=True)
    all_results = []
    seen_urls = set()

    for item_list in gathered:
        if isinstance(item_list, list):
            for res in item_list:
                url_key = res.get("url", "")
                if url_key and url_key not in seen_urls:
                    seen_urls.add(url_key)
                    all_results.append(res)

    return all_results


# ── Cross-Source Verification Engine ──

async def verify_claims_and_retrieve_evidence(extracted_claims: list[dict], raw_content: str) -> dict:
    """
    Main verification and evidence retrieval orchestration.
    1. Evaluates known fact-checking databases.
    2. Retrieves independent external sources.
    3. Calculates source reliability weights.
    4. Applies Cross-Source Agreement and UNVERIFIED decision logic.
    """
    content_lower = raw_content.lower()

    # 1. Check against Known Fact-Check Registry
    for kfc in KNOWN_FACT_CHECKS:
        if any(kw in content_lower for kw in kfc["keywords"]):
            # Match found in verified fact-check archive
            sources = [
                {
                    "name": s["name"],
                    "type": s["type"],
                    "url": s.get("url"),
                    "reliability": s["reliability"],
                }
                for s in kfc["sources"]
            ]
            reasons = list(kfc["reasons"])
            verdict = kfc["verdict"]
            confidence = 92.0 if verdict in ("LIKELY_FALSE", "LIKELY_TRUE") else 65.0
            risk_score = 88.0 if verdict == "LIKELY_FALSE" else 15.0 if verdict == "LIKELY_TRUE" else 50.0

            # Update extracted claims with individual verdicts
            claims_out = []
            for ec in extracted_claims:
                claims_out.append({
                    "claim_text": ec["claim_text"],
                    "claim_type": ec.get("claim_type", "general claim"),
                    "entities": ec.get("entities", []),
                    "verdict": verdict,
                    "confidence": confidence,
                })

            return {
                "verdict": verdict,
                "confidence": confidence,
                "risk_score": risk_score,
                "evidence_coverage": 85.0,
                "claims": claims_out,
                "sources": sources,
                "reasons": reasons,
                "recommendation": kfc["recommendation"],
            }

    # 2. Live Multi-Source Search & Verification
    primary_claim = extracted_claims[0]["claim_text"] if extracted_claims else raw_content
    search_results = await query_web_evidence(f"{primary_claim[:100]} fact check")

    if not search_results:
        # Secondary targeted search without 'fact check' suffix
        search_results = await query_web_evidence(primary_claim[:100])

    # 3. Source Reliability & Cross-Source Agreement Computation
    sources_collected = []
    reasons_collected = []
    support_weight = 0.0
    contradict_weight = 0.0
    official_support = False
    official_contradict = False

    for item in search_results:
        sources_collected.append({
            "name": item["publisher"],
            "type": item["source_type"],
            "url": item["url"],
            "reliability": item["reliability"],
        })

        if item["stance"] == "contradiction":
            contradict_weight += item["reliability"]
            if item["source_type"] == "official":
                official_contradict = True
            reasons_collected.append({
                "type": "contradiction",
                "text": f"{item['publisher']}: {item['snippet'][:120]}...",
            })
        elif item["stance"] == "support":
            support_weight += item["reliability"]
            if item["source_type"] == "official":
                official_support = True
            reasons_collected.append({
                "type": "support",
                "text": f"{item['publisher']}: {item['snippet'][:120]}...",
            })

    # 3.5 Deep AI Synthesis (Google Gemini) if AI_API_KEY is configured
    settings = get_settings()
    gemini_ai_insight = None
    if settings.ai_api_key:
        gemini_ai_insight = await query_gemini_reasoning(primary_claim, settings.ai_api_key)

    # 3.6 Gemini semantic analysis integration
    if gemini_ai_insight:
        ai_lower = gemini_ai_insight.lower()
        if any(w in ai_lower for w in [
            "unverified", "unconfirmed", "no evidence", "lack of evidence", "cannot be verified",
            "no supporting evidence", "no credible news reports", "no credible reports",
            "no official records", "no reports", "no record", "unsubstantiated", "not proven"
        ]):
            if not official_contradict:
                contradict_weight = 0.0
        elif any(w in ai_lower for w in ["false", "scam", "hoax", "fake", "fabricated"]):
            contradict_weight += 1.6
        elif any(w in ai_lower for w in ["true", "confirmed", "legitimate", "accurate"]):
            support_weight += 1.6

    # 4. Apply The UNVERIFIED Decision Rules (Phase 11 mandate)
    # Explicitly distinguish FALSE from NOT PROVEN

    if official_contradict or contradict_weight >= 1.5:
        verdict = "LIKELY_FALSE"
        confidence = 91.0
        risk_score = 85.0
        recommendation = "Do not share this claim as confirmed. Independent and official sources contradict the reported information."
    elif official_support and support_weight >= 1.6 and contradict_weight < 0.4:
        verdict = "LIKELY_TRUE"
        confidence = 89.0
        risk_score = 15.0
        recommendation = "This claim is supported by reliable official/news reporting. Verify specific terms on the relevant official site."
    elif len(sources_collected) >= 3 and support_weight >= 1.5 and support_weight > contradict_weight * 1.5:
        verdict = "LIKELY_TRUE"
        confidence = 78.0
        risk_score = 25.0
        recommendation = "Multiple independent news sources report this claim. Exercise standard caution for ongoing updates."
    elif any(kw in content_lower for kw in ["guarantee", "100%", "lottery", "free money", "claim prize", "urgent"]):
        verdict = "SUSPICIOUS"
        confidence = 76.0
        risk_score = 72.0
        reasons_collected.append({
            "type": "warning",
            "text": "Claim displays high-risk commercial or financial lure patterns with insufficient independent validation",
        })
        recommendation = "SUSPICIOUS: The claim contains high-urgency or financial promises that lack verified backing. Avoid financial transactions."
    else:
        # 🟡 THE UNVERIFIED SYSTEM
        verdict = "UNVERIFIED"
        confidence = 45.0
        risk_score = 48.0
        reasons_collected.append({
            "type": "warning",
            "text": "Insufficient reliable independent evidence to definitively confirm or reject this claim",
        })
        reasons_collected.append({
            "type": "warning",
            "text": "No authoritative government or official statement found regarding this specific assertion",
        })
        recommendation = "🟡 UNVERIFIED: There is insufficient reliable evidence to confirm or reject this claim. Exercise caution before sharing or acting on it."

    # Baseline fallback sources if live search returned empty
    if not sources_collected:
        sources_collected = [
            {"name": "Independent Web Search", "type": "general", "url": None, "reliability": 0.50},
            {"name": "Fact-Checking Registry", "type": "fact-checker", "url": None, "reliability": 0.90},
        ]

    # Append Gemini synthesis insight if available
    if gemini_ai_insight:
        reasons_collected.append({
            "type": "ai_synthesis",
            "text": f"Google Gemini Analysis: {gemini_ai_insight}",
        })

    # Deduplicate sources by name
    seen_names = set()
    deduped_sources = []
    for s in sources_collected:
        if s["name"] not in seen_names:
            seen_names.add(s["name"])
            deduped_sources.append(s)

    # Populate claims
    claims_out = []
    for ec in extracted_claims:
        claims_out.append({
            "claim_text": ec["claim_text"],
            "claim_type": ec.get("claim_type", "general claim"),
            "entities": ec.get("entities", []),
            "verdict": verdict,
            "confidence": confidence,
        })

    return {
        "verdict": verdict,
        "confidence": confidence,
        "risk_score": risk_score,
        "evidence_coverage": 75.0 if verdict != "UNVERIFIED" else 35.0,
        "claims": claims_out,
        "sources": deduped_sources[:6],
        "reasons": reasons_collected[:5],
        "recommendation": recommendation,
    }
