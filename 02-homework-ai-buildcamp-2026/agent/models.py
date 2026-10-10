from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from agent.config import AgentConfig


def build_chat_model(config: AgentConfig) -> BaseChatModel:
    """Build a chat model for any supported provider from a "<provider>:<model>" string."""
    return init_chat_model(config.model, temperature=config.temperature)
