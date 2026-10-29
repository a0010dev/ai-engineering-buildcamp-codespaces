# Week 4 — Testing a DuckDB SQL agent

A PydanticAI agent that answers questions about January 2024 NYC yellow taxi
trips. It uses `gpt-4o-mini`, retrieves the database schema with `get_schema`,
executes queries with `run_sql`, and returns a structured `SQLResult`.

## Setup

Requirements: Python 3.14, `uv`, and `OPENAI_API_KEY` in the environment. In
GitHub Codespaces, the API key is supplied through Codespaces secrets.

From the repository root:

```bash
cd Week4
uv sync --locked
```

The first agent or test run downloads the
[January 2024 parquet file](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet)
and creates `Week4/taxi.db`. Both files are generated locally and excluded from
Git. Their paths are anchored to `Week4`, regardless of the working directory.

## Run the agent

From `Week4`:

```bash
uv run --locked python -m week4.sql_agent
```

This runs the example question about average trip distance for rides with two
passengers and prints the structured response.

## Run the tests

From `Week4`:

```bash
uv run --locked python -m pytest tests -v -s
```

Alternatively, from the repository root:

```bash
uv run --locked --package week4 python -m pytest Week4/tests -v -s
```

The suite contains eight tests:

- [`tests/test_agent.py`](tests/test_agent.py): Python assertions for the trip
  count and the order of tool calls.
- [`tests/test_judge.py`](tests/test_judge.py): six LLM judge tests covering
  average fares by hour, credit card tips, pickup locations, long trips,
  zero-passenger trips, and the busiest weekday.

The tests call the OpenAI API. Reference answers use the January 2024 dataset;
judge feedback may vary between runs.

## Cost tracking

[`tests/conftest.py`](tests/conftest.py) enables the temporary patch in
[`tests/patch_agent.py`](tests/patch_agent.py).
[`tests/cost_tracker.py`](tests/cost_tracker.py) accumulates usage for both the
SQL agent and the judge and prints an estimated USD total after the test run.
It includes cached input pricing and records each run once, including calls
through `run_sync`.

This tracker stores usage in memory for a sequential test run. A recorded run
passed all eight tests with an estimated total of **$0.003029**; the total
depends on token usage and the configured model prices.

## Reflection

See [`week4_testing_reflection.md`](week4_testing_reflection.md) for the test
that increased my confidence in the agent and the lesson I will take into the
capstone.
