import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_factcheck_api_key() -> str:
    return os.getenv("GOOGLE_FACTCHECK_API_KEY") or os.getenv("GOOGLE_FACT_CHECK_API_KEY") or ""


def search_fact_checks(claim: str) -> dict:
    """
    Search official Google Fact Check Tools API for verified claims.
    """
    api_key = get_factcheck_api_key()
    if not api_key:
        return {"claims": []}

    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": claim,
        "key": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=8.0)
        if response.status_code != 200:
            return {"error": response.text, "claims": []}
        data = response.json()
        if isinstance(data, dict) and "claims" not in data:
            data["claims"] = []
        return data
    except Exception as e:
        return {"error": str(e), "claims": []}
