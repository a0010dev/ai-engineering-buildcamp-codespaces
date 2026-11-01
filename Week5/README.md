# Week 5 — Monitoring a trivia agent with Logfire

A terminal trivia quizmaster built with **PydanticAI** and **gpt-4o-mini**.
It fetches categories and multiple-choice questions from Open Trivia DB,
asks one question at a time, and keeps the conversation history between turns.
Logfire records the agent runs, model requests, tool calls, token usage, and
session feedback.

## Setup

Requirements: Python 3.14, `uv`, and these GitHub Codespaces secrets:

- `OPENAI_API_KEY`: access to the model.
- `LOGFIRE_TOKEN`: a write token for the Logfire project.
- `LOGFIRE_READ_TOKEN`: a read token for querying traces in the notebook.

Secrets are read from the environment. Do not put their values in source files
or notebook cells. Rebuild or restart the Codespace after adding secrets, and
restart an existing notebook kernel if necessary.

From the repository root, install the workspace dependencies:

```bash
uv sync --locked --all-packages
```

## Play a monitored session

From the repository root:

```bash
uv run --locked --package week5 python Week5/trivia_agent.py
```

The agent starts five easy Science & Nature questions. Answer each question,
then type `stop` to leave the conversation loop. Choose **Good**, **Bad**, or
**Skip** when prompted for feedback.

[`trivia_agent.py`](trivia_agent.py) enables monitoring with:

```python
logfire.configure()
logfire.instrument_pydantic_ai()
```

The entire conversation and feedback prompt run inside
`logfire.span('trivia_session')`. Each `agent.run_sync()` creates a child
`invoke_agent agent` span, displayed as `agent run` in the dashboard. A typical
five-question session has six runs: the initial prompt and five answers.
Model requests and tool calls appear underneath their corresponding runs.

Feedback is recorded with `logfire.info('user_feedback', feedback=feedback)`:
`1` means positive, `-1` means negative, and Skip sends no event. Because the
event is emitted inside the session span, it inherits the same trace context.
When recording an event outside that block, use `logfire.attach_context()`
with the saved session context.

## Query traces, reconstruct runs, and calculate costs

Open [`analyze_traces.ipynb`](analyze_traces.ipynb) using the repository's
existing Python environment. Run the cells in order to:

1. Configure the query client using `LOGFIRE_READ_TOKEN` and a date range in
   `Europe/Madrid`.
2. List completed `trivia_session` spans and select the session's `trace_id`.
3. Cross-check that identifier and timestamp with the Logfire dashboard.
4. Fetch every agent-run span in the trace and reconstruct an `AgentRunResult`
   for each run using [`trace_replay`](trace_replay/).
5. Sum the run token counts and calculate the session's estimated cost.
6. Count positive and negative `user_feedback` log events across sessions.

Adjust the date ranges and `session_index` for the sessions you want to inspect.
The final cell closes the query client; recreate it before repeating earlier
queries after that cell has run.

The notebook accepts both the older `gen_ai.usage.*` attributes and the current
`gen_ai.aggregated_usage.*` attributes on agent-run spans. It sums each run once,
without adding the model-request token counts again.

The `trace_replay` folder was copied from the
[lesson repository](https://github.com/alexeygrigorev/ai-engineering-buildcamp-code/tree/4550c847f8173a837bae6e88cee007756a8b9b4c/documentation-agent/trace_replay).
Its original `fetch_trace()` keeps only the latest run in a trace, so the
notebook queries all matching runs directly before converting them. Message
reconstruction is lossy and does not recreate every original runtime field.

## Recorded results

The grouped Q4 session stored in the notebook used **5,692 input tokens** and
**816 output tokens**. At the homework prices of **$0.15 per million input
tokens** and **$0.60 per million output tokens**, its estimated cost was
**$0.00134340 USD**.

The saved feedback query returned **2 positive** and **1 negative** events.
These counts cover the query's date range, rather than only the Q4 session.
New sessions and different query periods will produce different results.

## Reflection

See [`week5_monitoring_reflection.md`](week5_monitoring_reflection.md) for the
main lessons and how the collected data can support evaluation.
