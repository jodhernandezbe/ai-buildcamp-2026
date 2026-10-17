"""Cost tracking: wraps Agent.run so every run (agent and judge) is recorded."""

from dataclasses import dataclass, field
from decimal import Decimal

from pydantic_ai.agent import AbstractAgent


@dataclass
class UsageTracker:
    """Accumulates token usage and cost across all agent runs in a test session."""

    runs: int = 0
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: Decimal = field(default_factory=Decimal)

    def record(self, usage) -> None:
        self.runs += 1
        self.requests += usage.requests
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens
        self.cost += usage.cost or Decimal(0)


tracker = UsageTracker()
_original_run = AbstractAgent.run


async def _tracked_run(self, *args, **kwargs):
    result = await _original_run(self, *args, **kwargs)
    tracker.record(result.usage)
    return result


def patch_agent() -> None:
    """Replace AbstractAgent.run with the tracking wrapper (idempotent)."""
    AbstractAgent.run = _tracked_run


def unpatch_agent() -> None:
    AbstractAgent.run = _original_run
