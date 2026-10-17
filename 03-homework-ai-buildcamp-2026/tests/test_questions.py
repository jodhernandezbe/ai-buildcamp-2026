"""Scenario tests: one question per case, with ground truth taken from DuckDB.

Each case checks three things:
  1. columns  - the SQL must reference the columns the question depends on
  2. tools    - get_schema is called first, then run_sql
  3. answer   - result_text contains the known value (any listed spelling)
"""

import pytest

from agent import build_agent
from tests.utils import collect_tools

CASES = [
    pytest.param(
        "What is the average tip amount for credit card payments?",
        # payment_type = 1 is credit card; AVG(tip_amount) = 4.1697
        ["tip_amount", "payment_type"],
        ["4.17"],
        id="avg_tip_credit_card",
    ),
    pytest.param(
        "Which pickup location (PULocationID) has the most trips?",
        # PULocationID 132 has 145,240 trips (161 is second with 143,471)
        ["PULocationID"],
        ["132"],
        id="top_pickup_location",
    ),
    pytest.param(
        "What is the average fare for trips longer than 10 miles?",
        # AVG(fare_amount) WHERE trip_distance > 10 = 62.8808
        ["fare_amount", "trip_distance"],
        ["62.88"],
        id="avg_fare_long_trips",
    ),
    pytest.param(
        "How many trips had zero passengers recorded?",
        # passenger_count = 0 -> 31,465 (NULL passenger_count rows are a separate group)
        ["passenger_count"],
        ["31465"],
        id="zero_passengers",
    ),
    pytest.param(
        "What is the busiest day of the week for taxi trips?",
        # Wednesday: 495,032 trips (Tuesday is second with 463,664)
        ["tpep_pickup_datetime"],
        ["Wednesday"],
        id="busiest_weekday",
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("question, columns, expected", CASES)
async def test_question(question, columns, expected):
    result = await build_agent().run(question)
    output = result.output

    # columns: the query is built on the right fields
    sql = output.sql_query.lower()
    for column in columns:
        assert column.lower() in sql, f"{column} missing from SQL: {output.sql_query}"

    # tools: schema first, then SQL
    tools = collect_tools(result)
    assert tools[0] == "get_schema", f"tool order was {tools}"
    assert "run_sql" in tools, f"tool order was {tools}"

    # answer: known value appears (ignore thousands separators and case)
    text = output.result_text.replace(",", "").lower()
    assert any(value.lower() in text for value in expected), (
        f"expected one of {expected} in: {output.result_text}"
    )
