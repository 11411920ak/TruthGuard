import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_tavily_api_key() -> str:
    return os.getenv("TAVILY_API_KEY") or ""


def search_tavily(query: str, max_results: int = 5) -> dict:
    """
    Search Tavily AI Deep Search API for real-time web intelligence.
    """
    api_key = get_tavily_api_key()
    if not api_key:
        return {"results": []}

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
    }

    try:
        response = requests.post(url, json=payload, timeout=8.0)
        if response.status_code != 200:
            return {"error": response.text, "results": []}
        return response.json()
    except Exception as e:
        return {"error": str(e), "results": []}
