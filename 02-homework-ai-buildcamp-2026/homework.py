"""CLI that prints the answer to each homework question.

Usage:
    uv run python homework.py --question 1   # one question (1, 2, 3, 5 or 6)
    uv run python homework.py                # every question
    uv run python homework.py --help
"""

import argparse
from collections.abc import Callable

from agent import build_agent
from tools.wikipedia import get_page, search_wikipedia

CONCISE_HINT = " Answer concisely, in 2-3 sentences."
Q5_QUESTION = "What is this page about? https://en.wikipedia.org/wiki/Capybara" + CONCISE_HINT
Q6_QUESTION = "What are the main threats to capybara populations?"


def run_agent(question: str) -> tuple[list[tuple[str, dict]], str]:
    """Run the agent once; return its tool calls (in order) and its final answer."""
    result = build_agent().invoke({"messages": [("user", question)]})
    messages = result["messages"]
    tool_calls = [
        (call["name"], call["args"])
        for message in messages
        if message.type == "ai"
        for call in message.tool_calls
    ]
    return tool_calls, messages[-1].content


def format_tool_calls(tool_calls: list[tuple[str, dict]]) -> str:
    return "\n".join(f"  {i}. {name}({args})" for i, (name, args) in enumerate(tool_calls, 1))


def q1() -> str:
    results = search_wikipedia("capybara")
    return f"Total search results: {len(results)}"


def q2() -> str:
    titles = [result["title"] for result in search_wikipedia("capybara")]
    matches = [title for title in titles if "capybara" in title.lower()]
    return f"Titles containing 'capybara': {len(matches)} of {len(titles)}\n" + "\n".join(
        f"  - {title}" for title in matches
    )


def q3() -> str:
    return f"Characters in the 'Capybara' page: {len(get_page('Capybara'))}"


def q5() -> str:
    tool_calls, answer = run_agent(Q5_QUESTION)
    return f"Tool calls:\n{format_tool_calls(tool_calls)}\n\nMain topic according to the agent:\n{answer}"


def q6() -> str:
    tool_calls, answer = run_agent(Q6_QUESTION)
    return (
        f"Total tool calls: {len(tool_calls)}\n{format_tool_calls(tool_calls)}\n\n"
        f"Final answer:\n{answer}"
    )


QUESTIONS: dict[str, tuple[str, Callable[[], str]]] = {
    "1": ("Total results for the query 'capybara'", q1),
    "2": ("Results with 'capybara' in the title", q2),
    "3": ("Characters in the 'Capybara' page", q3),
    "5": ("Agent: what is the Capybara page about?", q5),
    "6": ("Agent: main threats to capybara populations", q6),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print the answers to the homework questions.")
    parser.add_argument(
        "-q",
        "--question",
        choices=[*QUESTIONS, "all"],
        default="all",
        help="question to answer (default: all). "
        + "; ".join(f"{key}: {title}" for key, (title, _) in QUESTIONS.items()),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    keys = list(QUESTIONS) if args.question == "all" else [args.question]
    for key in keys:
        title, answer_fn = QUESTIONS[key]
        print(f"=== Q{key}: {title} ===")
        print(answer_fn(), end="\n\n")


if __name__ == "__main__":
    main()
