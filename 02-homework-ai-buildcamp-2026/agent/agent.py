from collections.abc import Sequence
from datetime import date

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from agent.config import AgentConfig
from agent.models import build_chat_model
from agent.prompts import PromptRegistry
from agent.tool_registry import build_tools


def build_agent(
    model: BaseChatModel | None = None,
    tools: Sequence[BaseTool] | None = None,
    config: AgentConfig | None = None,
    prompts: PromptRegistry | None = None,
):
    """Assemble the agent. Model, tools and prompts can be injected (e.g. fakes in tests)."""
    config = config or AgentConfig()
    prompts = prompts or PromptRegistry()
    system_prompt = prompts.get(config.system_prompt).render(today=date.today().isoformat())
    return create_agent(
        model=model or build_chat_model(config),
        tools=list(tools) if tools is not None else build_tools(),
        system_prompt=system_prompt,
    )
