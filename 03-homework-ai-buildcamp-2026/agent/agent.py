from pydantic_ai import Agent

from agent.models import SQLResult
from tools.sql import SQLTools

INSTRUCTIONS = """\
You are a data analyst answering questions about NYC yellow taxi trips (January 2024).
The data lives in a DuckDB table called `trips`.

Always start by calling get_schema to see the available columns and types before
writing any query. Then use run_sql to answer the question. If a query fails,
read the error, fix the query and try again.

Only the first 50 rows of a result are shown, so prefer aggregations (COUNT, AVG,
GROUP BY) and LIMIT over selecting raw rows.
"""


def build_agent(sql_tools: SQLTools | None = None) -> Agent[None, SQLResult]:
    tools = sql_tools if sql_tools is not None else SQLTools()
    return Agent(
        "openai:gpt-4o-mini",
        instructions=INSTRUCTIONS,
        output_type=SQLResult,
        tools=[tools.get_schema, tools.run_sql],
    )


if __name__ == "__main__":
    question = "What's the average trip distance for rides with 2 passengers?"
    result = build_agent().run_sync(question)
    print(result.output.model_dump_json(indent=2))
    print(result.usage)
    for message in result.all_messages():
        for part in message.parts:
            if part.part_kind == "tool-call":
                print(f"tool call: {part.tool_name}({part.args})")
