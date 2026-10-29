from week4.sql_agent import agent
from week4.sql_tools import setup_database
from tests.utils import collect_tools


def test_trips_with_more_than_five_passengers():
    setup_database()

    result = agent.run_sync("How many trips had more than 5 passengers?")
    output = result.output

    assert isinstance(output.sql_query, str)
    assert output.sql_query.strip()
    # Verified directly: SELECT COUNT(*) FROM trips WHERE passenger_count > 5
    assert "22413" in output.result_text


def test_most_common_payment_type():
    setup_database()

    result = agent.run_sync("What is the most common payment type?")
    tools = collect_tools(result.all_messages())

    assert tools[0].name == "get_schema"
    assert any(tool.name == "run_sql" for tool in tools)

    print(f"Question4: {tools[1].name}")  # Nom de la segona eina que ha cridat
