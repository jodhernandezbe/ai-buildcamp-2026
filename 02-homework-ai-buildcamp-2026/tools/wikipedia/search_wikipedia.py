from tools.wikipedia.wikipedia_client import API_URL, wikipedia_get


def search_wikipedia(query: str) -> list[dict]:
    """Search Wikipedia for pages related to a query.

    Args:
        query (str): The search term (for example, "lesser capybara").

    Returns:
        list[dict]: The search results; each dict has "title" (str), "pageid" (int),
            "snippet" (str), etc.
    """
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
    }
    return wikipedia_get(API_URL, params).json()["query"]["search"]
