import json
import os
import sys
from datetime import datetime, timedelta, timezone

from logfire.query_client import LogfireQueryClient

from tools.trace_replay import TraceData, trace_to_run_result

MODEL_PRICES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

MODEL_NAME = "gpt-4o-mini"


def calculate_cost(model_name, input_tokens, output_tokens):
    prices = MODEL_PRICES[model_name.lower()]
    input_cost = (input_tokens / 1_000_000) * prices["input"]
    output_cost = (output_tokens / 1_000_000) * prices["output"]
    return input_cost + output_cost


def fetch_session(trace_id: str, client: LogfireQueryClient) -> TraceData:
    """Read every agent run span in a grouped session and sum their tokens.

    The newest span's messages hold the full conversation, because each run
    receives the message history of the previous ones. Tokens are summed over
    all spans, since each run is billed separately.
    """
    rows = client.query_json_rows(
        sql=f"""
        SELECT
            attributes->'pydantic_ai.all_messages' as all_messages,
            coalesce(
                attributes->>'gen_ai.aggregated_usage.input_tokens',
                attributes->>'gen_ai.usage.input_tokens'
            ) as input_tokens,
            coalesce(
                attributes->>'gen_ai.aggregated_usage.output_tokens',
                attributes->>'gen_ai.usage.output_tokens'
            ) as output_tokens
        FROM records
        WHERE trace_id = '{trace_id}'
          AND (span_name = 'agent run' OR span_name LIKE 'invoke_agent %')
        ORDER BY start_timestamp DESC
        """,
        min_timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    )['rows']

    if not rows:
        raise ValueError(f'No agent run spans found for trace_id={trace_id}')

    all_messages = rows[0]['all_messages']
    if isinstance(all_messages, str):
        all_messages = json.loads(all_messages)

    return TraceData(
        all_messages=all_messages,
        input_tokens=sum(int(r['input_tokens'] or 0) for r in rows),
        output_tokens=sum(int(r['output_tokens'] or 0) for r in rows),
    )


if __name__ == "__main__":
    trace_id = sys.argv[1] if len(sys.argv) > 1 else "01a173129e37226f6303d85a6004905f"

    client = LogfireQueryClient(read_token=os.environ['LOGFIRE_READ_TOKEN'])
    trace = fetch_session(trace_id, client)
    result = trace_to_run_result(trace)

    usage = result.usage
    cost = calculate_cost(MODEL_NAME, usage.input_tokens, usage.output_tokens)

    print(f"trace_id: {trace_id}")
    print(f"messages in conversation: {len(result.all_messages())}")
    print(f"input tokens: {usage.input_tokens}")
    print(f"output tokens: {usage.output_tokens}")
    print(f"approximate cost: ${cost:.6f}")
