"""Capture usage automatically for agent runs made during a test."""

from functools import wraps

from pydantic_ai import Agent

from tests.cost_tracker import capture_usage


def patch_agent(monkeypatch):
    original_run = Agent.run

    @wraps(original_run)
    async def tracked_run(self, *args, **kwargs):
        result = await original_run(self, *args, **kwargs)

        model = self.model
        model_name = f"{model.system}:{model.model_name}"
        capture_usage(model_name, result.usage)

        return result

    # run_sync delegates to run, so patching run alone avoids double counting.
    monkeypatch.setattr(Agent, "run", tracked_run)
