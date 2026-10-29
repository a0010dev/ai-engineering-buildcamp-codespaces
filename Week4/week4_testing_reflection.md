# Week 4 — Testing a SQL agent and evaluating its answers

During Week 4 of the AI Engineering Buildcamp, I added tests to a taxi-data
agent built with **PydanticAI**, **DuckDB**, and **OpenAI's gpt-4o-mini**. The
agent answers questions by inspecting the database schema and running SQL over
the January 2024 yellow taxi trip data.

One test that increased my confidence started with a simple question:
**"What is the most common payment type?"** I extracted the tool calls from the
agent's message history and checked:

```python
tools = collect_tools(result.all_messages())

assert tools[0].name == "get_schema"
assert any(tool.name == "run_sql" for tool in tools)
```

In the recorded run, the first tool was `get_schema` and the second was
`run_sql`. This gave me concrete evidence that the agent followed the expected
workflow for that question. The test makes that requirement repeatable, although
it does not independently verify that the SQL or final answer is correct.

My main lesson is to match each check to the evidence it needs. Python
assertions work well for precise requirements such as tool order. An LLM judge
lets me express criteria about the SQL and the response in natural language,
but it still needs reliable evidence or reference answers to assess correctness.
Our judge receives the answer and tool calls; it does not independently query
the database.

All **8 tests passed** in one full run. Tracking both the SQL agent and the
judge recorded **10,490 input tokens**, **2,426 output tokens**, and an estimated
total cost of **$0.003029** for that execution.

For my capstone, I will keep representative questions, check critical tool
behavior directly, and review judge decisions against known reference answers.

Tests: [`tests/test_agent.py`](tests/test_agent.py) and
[`tests/test_judge.py`](tests/test_judge.py)

Course: <https://maven.com/alexey-grigorev/from-rag-to-agents>
