from tools.wikipedia.wikipedia_client import INDEX_URL, wikipedia_get


def get_page(title: str) -> str:
    """Fetch the raw content of a Wikipedia page.

    Args:
        title (str): The exact title of the Wikipedia page (for example, "Capybara").

    Returns:
        str: The raw wikitext of the page.
    """
    params = {"title": title, "action": "raw"}
    return wikipedia_get(INDEX_URL, params).text
