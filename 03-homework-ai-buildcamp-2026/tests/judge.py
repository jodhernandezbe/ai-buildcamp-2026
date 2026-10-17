"""LLM judge: grades an agent run against natural-language criteria."""

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult

from agent import SQLResult
from tests.utils import collect_tools

JUDGE_MODEL = "openai:gpt-4o-mini"

JUDGE_INSTRUCTIONS = """\
You are a strict evaluator of an AI agent's work.
You receive the user's question, the agent's final output (SQL query and result)
and the tools the agent called. Judge each criterion independently using only that
evidence. A criterion passes only if the evidence clearly satisfies it; give a
short reason for every verdict.
"""


class CriterionResult(BaseModel):
    criterion: str = Field(description="The criterion, copied verbatim")
    passed: bool = Field(description="True only if the evidence clearly satisfies it")
    reason: str = Field(description="One or two sentences explaining the verdict")


class JudgeResult(BaseModel):
    results: list[CriterionResult]


judge_agent = Agent(
    JUDGE_MODEL,
    instructions=JUDGE_INSTRUCTIONS,
    output_type=JudgeResult,
)


async def evaluate_agent_performance(
    question: str,
    result: AgentRunResult[SQLResult],
    criteria: list[str],
) -> JudgeResult:
    """Ask the judge to grade the agent's run against each criterion."""
    numbered = "\n".join(f"{i}. {c}" for i, c in enumerate(criteria, 1))
    prompt = (
        f"<question>\n{question}\n</question>\n\n"
        f"<agent_output>\n{result.output.model_dump_json(indent=2)}\n</agent_output>\n\n"
        f"<tools_called>\n{', '.join(collect_tools(result))}\n</tools_called>\n\n"
        f"<criteria>\n{numbered}\n</criteria>"
    )
    judged = await judge_agent.run(prompt)
    return judged.output


def assert_criteria(judgement: JudgeResult, criteria: list[str]) -> None:
    """Fail with the judge's reasons unless every criterion passed."""
    assert len(judgement.results) == len(criteria), (
        f"Judge returned {len(judgement.results)} verdicts for {len(criteria)} criteria"
    )
    failures = [r for r in judgement.results if not r.passed]
    assert not failures, "Criteria failed:\n" + "\n".join(
        f"- {r.criterion}: {r.reason}" for r in failures
    )
