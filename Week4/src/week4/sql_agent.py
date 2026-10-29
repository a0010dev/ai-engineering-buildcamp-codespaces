from pydantic import BaseModel
from pydantic_ai import Agent

from week4.sql_tools import SQLTools, setup_database


class SQLResult(BaseModel):
    sql_query: str
    result_text: str
    row_count: int


sql_tools = SQLTools()

agent = Agent(
    "openai:gpt-4o-mini",
    output_type=SQLResult,
    tools=[sql_tools.get_schema, sql_tools.run_sql],
    instructions=(
        "You answer questions about taxi trips using DuckDB SQL. "
        "Always start by calling get_schema before running any queries. "
        "Use the schema to write SQL, then call run_sql to get actual results. "
        "Return the executed SQL in sql_query. Copy the complete run_sql "
        "response verbatim into result_text, including column headers, data "
        "rows, and the rows-returned line. Set row_count to the number of data "
        "rows returned by the tool (at most 50), not the number of trips used "
        "in an aggregate."
    ),
)


if __name__ == "__main__":
    setup_database()
    result = agent.run_sync(
        "What's the average trip distance for rides with 2 passengers?"
    )
    print(result.output.model_dump_json(indent=2))
