import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_newsapi_key() -> str:
    return os.getenv("NEWS_API_KEY") or os.getenv("NEWSAPI_KEY") or ""


def search_news(query: str, page_size: int = 5) -> dict:
    """
    Search live journalistic news articles via NewsAPI (https://newsapi.org).
    Returns matched articles with titles, publishers, URLs, and descriptions.
    """
    api_key = get_newsapi_key()
    if not api_key:
        return {"status": "error", "message": "NEWS_API_KEY is not configured", "articles": []}

    url = "https://newsapi.org/v2/everything"
    headers = {
        "X-Api-Key": api_key,
        "User-Agent": "TruthGuard-FactChecker/1.0",
    }
    params = {
        "q": query,
        "pageSize": max(1, min(page_size, 20)),
        "sortBy": "relevancy",
        "language": "en",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=8.0)
        if response.status_code != 200:
            return {
                "status": "error",
                "error": response.text,
                "articles": [],
            }
        data = response.json()
        if isinstance(data, dict) and "articles" not in data:
            data["articles"] = []
        return data
    except Exception as e:
        return {"status": "error", "error": str(e), "articles": []}
