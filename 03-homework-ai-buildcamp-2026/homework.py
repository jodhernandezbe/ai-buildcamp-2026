"""CLI that prints the answer to each homework question.

Usage:
    uv run python homework.py --question 1   # one question (1 to 6)
    uv run python homework.py                # every question
    uv run python homework.py --help
"""

import argparse
import asyncio
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from agent import build_agent
from tests.judge import evaluate_agent_performance
from tests.utils import collect_tools
from tools.sql import SQLTools
from tools.sql.setup import setup_database

HERE = Path(__file__).resolve().parent

Q2_QUESTION = "What's the average trip distance for rides with 2 passengers?"
Q3_QUESTION = "How many trips had more than 5 passengers?"
Q4_QUESTION = "What is the most common payment type?"
Q5_QUESTION = "Which hour of the day has the highest average fare amount?"
Q5_CRITERIA = [
    "the SQL query correctly calculates average fare by hour of day",
    "the result identifies a specific hour as having the highest average fare",
    "the result includes the actual average fare amount",
]


def q1() -> str:
    return f"Rows in the trips table: {setup_database():,}"


def q2() -> str:
    output = asyncio.run(build_agent().run(Q2_QUESTION)).output
    return f"SQL: {output.sql_query}\nAnswer: {output.result_text}"


def q3() -> str:
    async def ask():
        result = await build_agent().run(Q3_QUESTION)
        return result.output

    output = asyncio.run(ask())
    expected = SQLTools().run_sql("SELECT COUNT(*) FROM trips WHERE passenger_count > 5")
    return (
        f"Ground truth (DuckDB): {expected.splitlines()[1]}\n"
        f"Agent SQL: {output.sql_query}\nAgent answer: {output.result_text}"
    )


def q4() -> str:
    result = asyncio.run(build_agent().run(Q4_QUESTION))
    tools = collect_tools(result)
    return f"Tool calls in order: {tools}\nSecond tool: {tools[1]}"


def q5() -> str:
    async def ask():
        result = await build_agent().run(Q5_QUESTION)
        judgement = await evaluate_agent_performance(Q5_QUESTION, result, Q5_CRITERIA)
        return result.output, judgement

    output, judgement = asyncio.run(ask())
    verdicts = "\n".join(
        f"  [{'PASS' if r.passed else 'FAIL'}] {r.criterion}\n         {r.reason}"
        for r in judgement.results
    )
    return f"Agent answer: {output.result_text}\n\nJudge verdicts:\n{verdicts}"


def q6() -> str:
    """Run the whole test suite; conftest.py prints the token and cost summary."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    lines = proc.stdout.splitlines()
    start = next((i for i, line in enumerate(lines) if "LLM usage" in line), 0)
    return "\n".join(lines[start:])


QUESTIONS: dict[str, tuple[str, Callable[[], str]]] = {
    "1": ("Rows in the trips table", q1),
    "2": ("Agent: average trip distance for 2-passenger rides", q2),
    "3": ("Test: trips with more than 5 passengers", q3),
    "4": ("Test: tool call order for the most common payment type", q4),
    "5": ("LLM judge: hour with the highest average fare", q5),
    "6": ("Total cost of the test suite", q6),
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
