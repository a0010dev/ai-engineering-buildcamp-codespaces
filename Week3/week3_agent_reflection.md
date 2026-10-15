# Week 3 — Wikipedia tools and an agent with PydanticAI

During Week 3 of the AI Engineering Buildcamp, I built a Wikipedia agent with
**PydanticAI**, using **OpenAI** and the `gpt-4o-mini` model. I connected two Python
functions: `search_wikipedia` to find page titles and `get_page` to retrieve a
page's raw wikitext.

## What I learned

- A tool starts as a regular Python function. Calling Wikipedia and counting
  characters with `len(content)` do not require an LLM. The agent adds the ability
  to choose which function to call, supply its arguments, and use the result.
- Requests need the Wikipedia `User-Agent` header. Using `params`, a timeout,
  and `raise_for_status()` makes the HTTP calls easier to maintain and diagnose.
- Passing `tools=[search_wikipedia, get_page]` when creating the agent
  registers the existing functions with PydanticAI, following the course
  examples. Their type annotations and docstrings describe the tools, so I did
  not need to maintain a separate JSON tool schema for this agent.
- `result.output` contains the final answer. Inspecting `result.new_messages()`
  reveals the `ToolCallPart` requests, their arguments, and the corresponding
  `ToolReturnPart` results. I count calls once, rather than counting both a
  request and its return.
- Page length in characters differs from model input length in tokens. If page
  content exceeds the available context, I will need to select relevant sections
  or chunks before sending it to the model.

Notebook: [`introduction.ipynb`](introduction.ipynb)

Course: <https://maven.com/alexey-grigorev/from-rag-to-agents>
