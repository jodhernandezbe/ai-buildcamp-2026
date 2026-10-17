# Homework 3 (Week 4): AI Engineering Buildcamp - SQL Agent and Tests

This folder contains the third homework. The goal is to build a simple SQL agent
that answers questions about NYC yellow taxi trips (January 2024) using DuckDB,
then test it: exact-value checks, tool-call order, an LLM judge, and cost tracking.
It uses PydanticAI as the framework and OpenAI (`gpt-4o-mini`) as the provider.

## Structure

```
03-homework-ai-buildcamp-2026/
  data/                      parquet file and taxi.db (generated, git-ignored)
  tools/
    sql/
      setup.py               downloads the parquet file and loads the `trips` table
      sql_tools.py           SQLTools: get_schema() and run_sql(query)
  agent/
    models.py                SQLResult: sql_query, result_text, row_count
    agent.py                 build_agent(): model, instructions, output type, tools
  tests/
    utils.py                 collect_tools(): tool names the agent called, in order
    judge.py                 LLM judge: evaluate_agent_performance, assert_criteria
    patch_agent.py           wraps Agent.run to record tokens and cost
    conftest.py              enables the patch and prints the usage summary
    test_agent.py            exact count, tool order, and LLM-judge tests
    test_questions.py        five parametrized scenario tests
  homework.py                prints the answer to each homework question
```

## Design notes

- **The database is read-only for the agent.** `SQLTools` opens `taxi.db` with
  `read_only=True`, so a generated query cannot modify the data.
- **SQL errors go back to the model.** `run_sql` returns the DuckDB error as text
  instead of raising, so the agent can fix the query and retry.
- **Results are capped at 50 rows.** The instructions tell the agent to prefer
  aggregations and `LIMIT`.
- **The agent must read the schema first.** The instructions require
  `get_schema` before any query, and a test checks the order of tool calls.
- **Ground truth comes from DuckDB.** The data is static, so tests compare the
  agent's answer with values computed directly (see `test_questions.py`).
- **Cost tracking covers `Agent.run` only.** `run_sync` calls are not counted.

## Usage

Requires `OPENAI_API_KEY` in the environment. Run everything from this folder.

Load the data (downloads about 50 MB the first time):
```
python tools/sql/setup.py
```

Ask the agent a question:
```
python -m agent.agent
```

Run the tests (they call the OpenAI API and cost about $0.003 per run):
```
python -m pytest tests -v
```
Use `python -m pytest`, not plain `pytest`, so this folder is on the import path.

Print the answer to each homework question:
```
python homework.py [-q {1,2,3,4,5,6,all}]
```

| Question | What it answers |
|----------|-----------------|
| 1 | Rows in the `trips` table |
| 2 | Agent: average trip distance for 2-passenger rides |
| 3 | Trips with more than 5 passengers (agent vs. DuckDB ground truth) |
| 4 | Tool call order for the most common payment type |
| 5 | LLM judge: hour with the highest average fare |
| 6 | Token usage and total cost of the full test suite |

Questions 2 to 6 call an LLM, so wording, token counts, and cost can differ
slightly from run to run.
