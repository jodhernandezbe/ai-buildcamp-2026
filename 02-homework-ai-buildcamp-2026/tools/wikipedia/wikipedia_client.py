"""Shared HTTP plumbing for the Wikipedia tools (single place for URLs and headers)."""

import requests

API_URL = "https://en.wikipedia.org/w/api.php"
INDEX_URL = "https://en.wikipedia.org/w/index.php"
HEADERS = {"User-Agent": "ai-engineering-buildcamp/1.0 (educational project)"}
TIMEOUT_SECONDS = 10


def wikipedia_get(url: str, params: dict) -> requests.Response:
    """GET a Wikipedia endpoint with the required User-Agent; raise on HTTP errors."""
    response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response
