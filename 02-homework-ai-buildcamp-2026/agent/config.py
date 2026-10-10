import os
from dataclasses import dataclass, field

DEFAULT_MODEL = "openai:gpt-4o-mini"


@dataclass(frozen=True)
class AgentConfig:
    """Provider-agnostic agent settings.

    `model` uses LangChain's "<provider>:<model>" format, so switching provider
    (e.g. "anthropic:claude-sonnet-4-5") is a config change, not a code change.
    `system_prompt` is the name of a prompt in the PromptRegistry.
    """

    model: str = field(default_factory=lambda: os.getenv("AGENT_MODEL", DEFAULT_MODEL))
    temperature: float = 0.0
    system_prompt: str = "wikipedia_agent"
