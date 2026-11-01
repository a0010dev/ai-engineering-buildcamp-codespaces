# Week 5 — Monitoring a trivia agent with Logfire

During Week 5 of the AI Engineering Buildcamp, I added **Pydantic Logfire**
monitoring to a trivia agent built with **PydanticAI** and **gpt-4o-mini**.
The agent uses `get_categories` and `get_questions` to retrieve questions from
Open Trivia DB, then runs a conversation in the terminal.

My main takeaway is the difference between an agent run and a conversation.
Each call to `agent.run_sync()` creates an `invoke_agent agent` span. In a
five-question session, I observed six runs: one for the initial request and
one for each answer. A run can contain several model requests and tool calls;
those are child spans, rather than separate conversation turns.

Wrapping the conversation in `logfire.span('trivia_session')` grouped the runs
under one trace. This made it easier to inspect the complete interaction and
see the total token usage and cost. The recorded session used **5,692 input
tokens** and **816 output tokens**, for an estimated **$0.00134340 USD** at the
prices supplied in the homework.

I also added a feedback prompt after the conversation loop, while still inside
the session span. Positive and negative answers produce a `user_feedback` log
event with `feedback=1` or `feedback=-1`; Skip produces no event. The saved SQL
query counted **two positive events and one negative event**. Sharing the
session's trace context makes it possible to connect that feedback to the
conversation it describes, although a session-level rating does not identify
which individual answer caused the reaction.

The dashboard was useful for inspecting individual sessions. Querying Logfire
with SQL gave me a repeatable way to retrieve sessions, count feedback, and
prepare data for further analysis. I used a separate read token from the
environment and compared the queried trace ID with the dashboard.

Reconstructing the runs exposed two details that matter for reliable analysis.
The lesson module's `fetch_trace()` selects only the latest run, which misses
most of the usage in a grouped session. The installed instrumentation also
stores run totals under `gen_ai.aggregated_usage.*`, while the example used
`gen_ai.usage.*`. The notebook handles both attribute names, reconstructs each
run separately, and sums its usage once. Adding the child model-request totals
as well would count the same tokens twice.

For my capstone, I will use traces to understand actual agent behavior and
select representative interactions for evaluation. Negative feedback can help
find cases worth reviewing, but it is a signal for investigation rather than
proof that an answer is wrong. Reconstructing conversations lets me preserve
the context needed to assess those cases and turn useful examples into future
evaluation tests.

Agent: [`trivia_agent.py`](trivia_agent.py)

Analysis notebook: [`analyze_traces.ipynb`](analyze_traces.ipynb)

Course: <https://maven.com/alexey-grigorev/from-rag-to-agents>
