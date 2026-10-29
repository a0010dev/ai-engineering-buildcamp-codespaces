import pytest

from week4.sql_agent import agent as sql_agent
from week4.sql_tools import setup_database

from tests.utils import run_agent_test
from tests.judge import assert_criteria


TOOL_CRITERIA = [
    "the first tool call is 'get_schema'",
    "calls 'run_sql' after 'get_schema' to obtain actual query results",
]


@pytest.fixture(scope="module")
def agent():
    setup_database()
    return sql_agent


@pytest.mark.asyncio
async def test_highest_average_fare_by_hour(agent):
    user_prompt = 'Which hour of the day has the highest average fare amount?'
    result = await run_agent_test(agent, user_prompt)

    await assert_criteria(result, [
        "the SQL query correctly calculates average fare by hour of day",
        "the result identifies a specific hour as having the highest average fare",
        "the result includes the actual average fare amount",
    ])


@pytest.mark.asyncio
async def test_average_tip_for_credit_card_payments(agent):
    result = await run_agent_test(
        agent, "What is the average tip amount for credit card payments?"
    )

    await assert_criteria(result, [
        *TOOL_CRITERIA,
        "the SQL calculates AVG(tip_amount) and filters on payment_type = 1 "
        "for credit card payments",
        "the result includes the average tip amount, approximately 4.17; "
        "both the unrounded value 4.16967062749 and rounding to cents are valid",
    ])


@pytest.mark.asyncio
async def test_pickup_location_with_most_trips(agent):
    result = await run_agent_test(
        agent, "Which pickup location (PULocationID) has the most trips?"
    )

    await assert_criteria(result, [
        *TOOL_CRITERIA,
        "the SQL groups trips by PULocationID, counts the trips for each "
        "location, and selects the location with the highest count",
        "the result identifies PULocationID 132 as the location with the most trips",
    ])


@pytest.mark.asyncio
async def test_average_fare_for_trips_longer_than_ten_miles(agent):
    result = await run_agent_test(
        agent, "What is the average fare for trips longer than 10 miles?"
    )

    await assert_criteria(result, [
        *TOOL_CRITERIA,
        "the SQL calculates AVG(fare_amount) and restricts the calculation "
        "to trips where trip_distance > 10",
        "the result includes the average fare amount, approximately 62.88; "
        "both the unrounded value 62.88081242826 and rounding to cents are valid",
    ])


@pytest.mark.asyncio
async def test_trips_with_zero_passengers(agent):
    result = await run_agent_test(
        agent, "How many trips had zero passengers recorded?"
    )

    await assert_criteria(result, [
        *TOOL_CRITERIA,
        "the SQL counts trips by filtering on passenger_count = 0, "
        "without including NULL passenger counts as zero",
        "the result reports 31465 trips with zero passengers recorded",
    ])


@pytest.mark.asyncio
async def test_busiest_day_of_week(agent):
    result = await run_agent_test(
        agent, "What is the busiest day of the week for taxi trips?"
    )

    await assert_criteria(result, [
        *TOOL_CRITERIA,
        "the SQL groups trips by the day of the week derived from "
        "tpep_pickup_datetime, counts trips across all dates for each weekday, "
        "and selects the weekday with the highest trip count",
        "the result identifies Wednesday as the busiest day; the numeric "
        "value 3 is also valid when using DuckDB DOW, ISODOW, or strftime('%w')",
    ])
