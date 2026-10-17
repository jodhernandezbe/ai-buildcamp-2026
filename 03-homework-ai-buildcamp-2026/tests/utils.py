from pydantic_ai.agent import AgentRunResult

# PydanticAI exposes the structured output as a tool call with this name
OUTPUT_TOOL_NAME = "final_result"


def collect_tools(result: AgentRunResult) -> list[str]:
    """Return the names of the tools the agent called, in call order.

    The final structured-output call is excluded, so only real tools remain.
    """
    return [
        part.tool_name
        for message in result.all_messages()
        for part in message.parts
        if part.part_kind == "tool-call" and part.tool_name != OUTPUT_TOOL_NAME
    ]
