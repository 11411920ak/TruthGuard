import sys
import os
import httpx
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv("backend/.env")

fact_check_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")
serper_key = os.getenv("SEARCH_API_KEY", "")
tavily_key = os.getenv("TAVILY_API_KEY", "")
ai_key = os.getenv("AI_API_KEY", "")
news_key = os.getenv("NEWS_API_KEY", "")

test_query = "free laptop scheme"

print("=" * 60)
print("1. Testing Google Fact Check Tools API")
print("=" * 60)
try:
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={test_query}&key={fact_check_key}"
    r = httpx.get(url, timeout=10.0)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        claims = data.get("claims", [])
        print(f"✅ SUCCESS! Retrieved {len(claims)} official fact-checks.")
        for i, c in enumerate(claims[:2]):
            print(f"  [Claim {i+1}]: {c.get('text')}")
            for cr in c.get("claimReview", [])[:1]:
                print(f"    Publisher: {cr.get('publisher', {}).get('name')}")
                print(f"    Rating: {cr.get('textualRating')}")
                print(f"    URL: {cr.get('url')}")
    else:
        print(f"❌ FAILED: {r.text[:300]}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)
print("2. Testing Serper Google Search API")
print("=" * 60)
try:
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": serper_key, "Content-Type": "application/json"}
    payload = {"q": test_query, "num": 3}
    r = httpx.post(url, headers=headers, json=payload, timeout=10.0)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        organic = data.get("organic", [])
        print(f"✅ SUCCESS! Retrieved {len(organic)} live Google search results.")
        for i, res in enumerate(organic[:2]):
            print(f"  [Result {i+1}]: {res.get('title')}")
            print(f"    Snippet: {res.get('snippet')[:100]}...")
            print(f"    Link: {res.get('link')}")
    else:
        print(f"❌ FAILED: {r.text[:300]}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)
print("3. Testing Tavily AI Search API")
print("=" * 60)
try:
    url = "https://api.tavily.com/search"
    payload = {"api_key": tavily_key, "query": test_query, "max_results": 3}
    r = httpx.post(url, json=payload, timeout=10.0)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        results = data.get("results", [])
        print(f"✅ SUCCESS! Retrieved {len(results)} Tavily deep-search results.")
        for i, res in enumerate(results[:2]):
            print(f"  [Result {i+1}]: {res.get('title')}")
            print(f"    Snippet: {res.get('content')[:100]}...")
            print(f"    URL: {res.get('url')}")
    else:
        print(f"❌ FAILED: {r.text[:300]}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)
print("4. Testing AI API Key")
print("=" * 60)
# Let's test if ai_key works with Google Gemini or OpenAI
print(f"Key preview: {ai_key[:8]}... (length: {len(ai_key)})")

# Try Google Gemini with AI_API_KEY using gemini-flash-latest
try:
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={ai_key}"
    payload = {"contents": [{"parts": [{"text": "Is the claim 'Government gives free 5G recharge for 3 months to all users' true or false? Answer in 1 short sentence."}]}]}
    r = httpx.post(gemini_url, json=payload, timeout=12.0)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"✅ SUCCESS! Gemini Flash Response:\n   \"{text.strip()}\"")
    else:
        print(f"❌ Gemini Error: {r.text[:300]}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)
print("5. Testing News API Key")
print("=" * 60)
try:
    news_url = f"https://newsapi.org/v2/everything?q={test_query}&pageSize=3&sortBy=relevancy&language=en"
    headers = {
        "X-Api-Key": news_key,
        "User-Agent": "TruthGuard-Tester/1.0",
    }
    r = httpx.get(news_url, headers=headers, timeout=10.0)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        articles = data.get("articles", [])
        print(f"✅ SUCCESS! Retrieved {len(articles)} live journalistic news articles.")
        for i, art in enumerate(articles[:2]):
            print(f"  [Article {i+1}]: {art.get('title')}")
            print(f"    Publisher: {art.get('source', {}).get('name')}")
            print(f"    Snippet: {(art.get('description') or '')[:100]}...")
            print(f"    URL: {art.get('url')}")
    else:
        print(f"❌ FAILED: {r.text[:300]}")
except Exception as e:
    print(f"❌ ERROR: {e}")

