from collections.abc import Callable, Sequence

from langchain_core.tools import BaseTool, tool

from tools.wikipedia import get_page, search_wikipedia

# Single place to register tools. The functions in `tools/` stay framework-agnostic;
# LangChain only appears here, where they are wrapped.
WIKIPEDIA_TOOLS: tuple[Callable, ...] = (search_wikipedia, get_page)


def to_langchain_tools(functions: Sequence[Callable]) -> list[BaseTool]:
    """Wrap plain functions as LangChain tools.

    The name comes from the function, and the description and argument schema are
    parsed from its Google-style docstring.
    """
    return [tool(fn, parse_docstring=True) for fn in functions]


def build_tools() -> list[BaseTool]:
    return to_langchain_tools(WIKIPEDIA_TOOLS)
