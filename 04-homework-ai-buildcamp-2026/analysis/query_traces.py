import os
from datetime import datetime, timedelta, timezone

from logfire.query_client import LogfireQueryClient

client = LogfireQueryClient(read_token=os.environ['LOGFIRE_READ_TOKEN'])
since = datetime.now(timezone.utc) - timedelta(hours=3)

# Trace IDs of the grouped sessions (trivia_session root spans)
sessions_sql = """
select trace_id, start_timestamp
from records
where span_name = 'trivia_session'
order by start_timestamp desc
limit 10
"""

for row in client.query_json_rows(sessions_sql, min_timestamp=since)['rows']:
    print('SESSION', row['trace_id'], row['start_timestamp'])

# Input tokens per agent run inside each session trace
tokens_sql = """
select trace_id, attributes->>'gen_ai.aggregated_usage.input_tokens' as input_tokens
from records
where span_name = 'invoke_agent agent'
order by start_timestamp
"""

totals = {}
for row in client.query_json_rows(tokens_sql, min_timestamp=since)['rows']:
    totals.setdefault(row['trace_id'], []).append(int(row['input_tokens'] or 0))

for trace_id, values in totals.items():
    print('RUNS', trace_id, len(values), 'PER RUN', values, 'TOTAL', sum(values))
