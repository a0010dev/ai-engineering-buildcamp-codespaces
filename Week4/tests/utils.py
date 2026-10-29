from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ToolCall:
    name: str
    args: Dict[str, Any]


def collect_tools(messages):
    tool_calls = []

    for m in messages:
        for p in m.parts:
            if p.part_kind != "tool-call":
                continue

            if p.tool_name == "final_result":
                continue

            tool_calls.append(ToolCall(p.tool_name, p.args))

    return tool_calls


async def run_agent_test(agent, user_prompt):
    return await agent.run(user_prompt)
