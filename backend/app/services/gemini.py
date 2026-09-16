import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()


def get_gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY") or ""


def extract_claim_from_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """
    Uses Gemini Vision to inspect an uploaded image (e.g. Instagram screenshot, meme, news post)
    and extract the central factual claim and visible text.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return {"claim": "", "raw_text": "", "error": "No Gemini API key configured"}

    b64_data = base64.b64encode(image_bytes).decode("utf-8")

    for model in ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-flash-latest"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        prompt = (
            "You are a specialized fact-checking claim extraction AI. "
            "Examine this screenshot or image carefully (it may be an Instagram post, tweet, meme, or flyer). "
            "1. Extract the primary factual claim or central assertion being made.\n"
            "2. Extract any visible text.\n"
            "Respond strictly in this format:\n"
            "CLAIM: <one clear, concise sentence of the central claim>\n"
            "TEXT: <all readable text in the image>"
        )
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": mime_type, "data": b64_data}},
                ]
            }]
        }
        try:
            resp = requests.post(url, json=payload, timeout=12.0)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                claim = ""
                visible_text = ""
                for line in text.splitlines():
                    if line.startswith("CLAIM:"):
                        claim = line.replace("CLAIM:", "").strip()
                    elif line.startswith("TEXT:"):
                        visible_text = line.replace("TEXT:", "").strip()
                if not claim:
                    claim = text.split("\n")[0].strip()
                return {
                    "claim": claim,
                    "raw_text": visible_text or text,
                    "model": model,
                    "status": "success",
                }
        except Exception:
            continue

    return {"claim": "", "raw_text": "", "error": "Gemini Vision extraction unavailable"}


def analyze_claim_and_evidence(claim: str, fact_checks: list[dict], web_evidence: list[dict]) -> dict:
    """
    Uses Gemini to synthesize collected evidence from Google Fact Check and Tavily
    and produce an authoritative TruthGuard verdict, confidence, risk score, and explanation.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return {"analysis": "Gemini API key not configured.", "verdict": "UNVERIFIED"}

    # Format evidence context
    fc_context = ""
    for fc in fact_checks[:3]:
        publisher = fc.get("publisher", "Official Fact-Checker")
        rating = fc.get("rating", "Unrated")
        url_str = fc.get("url", "")
        fc_context += f"- Publisher: {publisher}, Rating: {rating}, Source: {url_str}\n"

    web_context = ""
    for we in web_evidence[:4]:
        title = we.get("title", "")
        snippet = we.get("snippet", "")
        web_context += f"- Title: {title}, Snippet: {snippet[:140]}...\n"

    prompt = f"""You are TruthGuard AI, an authoritative digital content verification system.
Evaluate this claim based on the gathered evidence:

CLAIM:
"{claim}"

EVIDENCE FROM GOOGLE FACT CHECK:
{fc_context or "No direct fact checks found."}

EVIDENCE FROM TAVILY SEARCH:
{web_context or "No search results found."}

INSTRUCTIONS:
1. Provide a verdict: choose strictly from [LIKELY_TRUE, LIKELY_FALSE, SUSPICIOUS, UNVERIFIED].
2. Provide a Confidence Score (0-100).
3. Provide a Risk Score (0-100).
4. Provide a 2-sentence explanation of why.

FORMAT:
VERDICT: <one of LIKELY_TRUE, LIKELY_FALSE, SUSPICIOUS, UNVERIFIED>
CONFIDENCE: <number>
RISK: <number>
EXPLANATION: <text>
"""
    for model in ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-flash-latest"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            resp = requests.post(url, json=payload, timeout=12.0)
            if resp.status_code == 200:
                data = resp.json()
                analysis_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

                verdict = "UNVERIFIED"
                confidence = 50.0
                risk_score = 50.0
                explanation = analysis_text

                for line in analysis_text.splitlines():
                    if line.startswith("VERDICT:"):
                        v = line.replace("VERDICT:", "").strip().upper()
                        if v in ("LIKELY_TRUE", "LIKELY_FALSE", "SUSPICIOUS", "UNVERIFIED"):
                            verdict = v
                    elif line.startswith("CONFIDENCE:"):
                        try:
                            confidence = float(line.replace("CONFIDENCE:", "").strip().replace("%", ""))
                        except Exception:
                            pass
                    elif line.startswith("RISK:"):
                        try:
                            risk_score = float(line.replace("RISK:", "").strip().replace("%", ""))
                        except Exception:
                            pass
                    elif line.startswith("EXPLANATION:"):
                        explanation = line.replace("EXPLANATION:", "").strip()

                return {
                    "verdict": verdict,
                    "confidence": confidence,
                    "risk_score": risk_score,
                    "explanation": explanation,
                    "full_analysis": analysis_text,
                    "model": model,
                }
        except Exception:
            continue

    return {"analysis": "Could not complete Gemini analysis.", "verdict": "UNVERIFIED"}
