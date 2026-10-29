"""Reset, enable, and report cost tracking for the sequential test suite."""

import pytest

from tests.cost_tracker import display_total_usage, reset_usage
from tests.patch_agent import patch_agent


def pytest_sessionstart(session):
    reset_usage()


@pytest.fixture(autouse=True)
def track_agent_costs(monkeypatch):
    patch_agent(monkeypatch)


def pytest_sessionfinish(session, exitstatus):
    display_total_usage()
