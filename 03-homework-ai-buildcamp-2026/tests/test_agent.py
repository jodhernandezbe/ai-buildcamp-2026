import pytest

from agent import build_agent
from tests.judge import assert_criteria, evaluate_agent_performance
from tests.utils import collect_tools

# SELECT COUNT(*) FROM trips WHERE passenger_count > 5  (January 2024 data, static)
EXPECTED_COUNT = 22413


@pytest.fixture
def agent():
    return build_agent()


@pytest.mark.asyncio
async def test_trips_with_more_than_5_passengers(agent):
    result = await agent.run("How many trips had more than 5 passengers?")
    output = result.output

    assert isinstance(output.sql_query, str)
    assert output.sql_query.strip() != ""

    # accept "22413" as well as "22,413"
    assert str(EXPECTED_COUNT) in output.result_text.replace(",", "")


@pytest.mark.asyncio
async def test_gets_schema_before_running_sql(agent):
    result = await agent.run("What is the most common payment type?")
    tools = collect_tools(result)

    assert tools[0] == "get_schema"
    assert "run_sql" in tools


@pytest.mark.asyncio
async def test_highest_average_fare_hour(agent):
    question = "Which hour of the day has the highest average fare amount?"
    criteria = [
        "the SQL query correctly calculates average fare by hour of day",
        "the result identifies a specific hour as having the highest average fare",
        "the result includes the actual average fare amount",
    ]

    result = await agent.run(question)
    judgement = await evaluate_agent_performance(question, result, criteria)

    assert_criteria(judgement, criteria)
