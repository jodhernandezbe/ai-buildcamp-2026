# Homework 4: AI Engineering Buildcamp - Trivia Agent and Tracing

This folder contains the fourth homework. The goal is a trivia quizmaster agent
that fetches questions from the Open Trivia DB, plays a session with the user,
and is monitored with Logfire: each session is grouped under one parent span,
its token usage and cost are read back from Logfire, and the user's feedback is
recorded in the same trace.

It uses PydanticAI as the framework and OpenAI (`gpt-4o-mini`) as the provider.

## Structure

```
04-homework-ai-buildcamp-2026/
  agent/
    trivia_agent.py        agent, instructions, run() loop, feedback, Logfire setup
  tools/
    trivia.py              TriviaTools: get_categories() and get_questions()
    trace_replay/          converter from Logfire trace data to PydanticAI results
  analysis/
    query_traces.py        lists sessions and input tokens per run from Logfire
    session_cost.py        rebuilds a session from its trace and computes its cost
  logs/                    console output of past runs (git-ignored)
```

## Design notes

- **One session, one parent span.** `run()` is wrapped in
  `logfire.span('trivia_session')`, so every `invoke_agent agent` run of the
  session is a child of the same trace.
- **Feedback stays in the trace.** `ask_feedback()` runs inside the session
  span, so the `trivia session feedback` event lands in the same trace.
- **Tokens are summed over the session.** `session_cost.py` reads every agent
  run span and adds up the tokens. The messages come from the newest span,
  because it holds the full conversation.
- **Logfire token attribute names.** Token counts are stored under
  `gen_ai.aggregated_usage.input_tokens` and `gen_ai.aggregated_usage.output_tokens`.
  The `trace_replay` converter from the lesson reads `gen_ai.usage.*`, which is
  empty for these runs, so `session_cost.py` reads the aggregated keys first.
- **Credentials.** Logfire credentials live in the repo root's `.logfire/`, and
  the OpenAI and Logfire read tokens live in the root `.env`. Neither is committed.

## Usage

Run these from the repo root, because Logfire looks for its credentials in the
current folder. Load the environment first:
```
cd /Users/josehernandez/Documents/ai-buildcamp-2026
set -a && . ./.env && set +a
```

Play a session (answer the questions, type `stop`, then give feedback):
```
PYTHONPATH=04-homework-ai-buildcamp-2026 uv run python 04-homework-ai-buildcamp-2026/agent/trivia_agent.py
```

List sessions and tokens per run:
```
PYTHONPATH=04-homework-ai-buildcamp-2026 uv run python 04-homework-ai-buildcamp-2026/analysis/query_traces.py
```

Compute the cost of one session (defaults to the grouped session; pass a trace ID to choose another):
```
PYTHONPATH=04-homework-ai-buildcamp-2026 uv run python 04-homework-ai-buildcamp-2026/analysis/session_cost.py [trace_id]
```

Run the `trace_replay` tests (no API calls):
```
cd 04-homework-ai-buildcamp-2026 && PYTHONPATH=. uv run --project .. python -m pytest tools/trace_replay -q
```

Pricing used for `gpt-4o-mini`: $0.15 per 1M input tokens, $0.60 per 1M output tokens.
