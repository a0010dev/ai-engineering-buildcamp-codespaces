"""Run recipe scenarios concurrently: python Week6/run_scenarios.py --workers 4."""

import argparse
import asyncio
import csv
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from tqdm.auto import tqdm
except ImportError:
    tqdm = None

BASE_DIR = Path(__file__).resolve().parent
MODEL = "gpt-4o-mini"
# Estimated USD per million tokens, retaining the original runner's rates.
MODEL_PRICES = {MODEL: {"input": 0.15, "output": 0.60}}


def calculate_cost(usage, model=MODEL):
    prices = MODEL_PRICES[model]
    return round(
        (usage.input_tokens * prices["input"]
         + usage.output_tokens * prices["output"]) / 1_000_000,
        6,
    )


def threaded_map(fn, items, max_workers=4):
    """Show completion progress while preserving input order in the output."""
    items = list(items)
    results = [None] * len(items)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fn, item): i for i, item in enumerate(items)}
        completed = as_completed(futures)
        if tqdm is not None:
            completed = tqdm(completed, total=len(items), desc="Scenarios")
        for count, future in enumerate(completed, 1):
            results[futures[future]] = future.result()
            if tqdm is None:
                print(f"Scenarios: {count}/{len(items)}", flush=True)
    return results


async def run_agent(question):
    from openai import AsyncOpenAI
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider
    from recipe_agent import agent

    # Each call owns its client and event loop; no async client crosses threads.
    async with AsyncOpenAI(timeout=60.0) as client:
        model = OpenAIChatModel(MODEL, provider=OpenAIProvider(openai_client=client))
        with agent.override(model=model):
            return await agent.run(question)


def run_scenario(scenario):
    start = time.perf_counter()
    output = {**scenario}
    try:
        result = asyncio.run(run_agent(scenario["question"]))
        usage = result.usage
        if callable(usage):  # Compatibility with older Pydantic AI releases.
            usage = usage()
        messages = json.loads(result.all_messages_json())
        output.update(
            status="ok",
            output=result.output,
            tools=[
                part
                for message in messages
                for part in message["parts"]
                if part["part_kind"] in {"tool-call", "tool-return"}
            ],
            messages=messages,
            tokens={
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens,
            },
            cost=calculate_cost(usage),
        )
    except Exception as exc:
        # Failed runs may still incur charges; their cost is unknown.
        # Store the exception class only, avoiding sensitive HTTP error details.
        output.update(status="error", output=None, error=type(exc).__name__, cost=None)
    output["execution_time"] = round(time.perf_counter() - start, 2)
    return output


def run_all(input_path=BASE_DIR / "scenarios.csv", output_path=BASE_DIR / "results.json",
            workers=4, limit=None):
    if workers < 1:
        raise ValueError("workers must be at least 1")
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1")
    with Path(input_path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"question", "category", "type"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV must contain question, category and type columns")
        scenarios = list(reader)
    for row_number, scenario in enumerate(scenarios, 2):
        if None in scenario or any(not scenario[key] or not scenario[key].strip()
                                   for key in required):
            raise ValueError(f"Invalid scenario at CSV row {row_number}")
    if limit is not None:
        scenarios = scenarios[:limit]

    results = threaded_map(run_scenario, scenarios, max_workers=workers)
    with Path(output_path).open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    failures = sum(row["status"] == "error" for row in results)
    total_cost = sum(row["cost"] or 0 for row in results)
    print(f"Saved {len(results)} results to {output_path} ({failures} errors)")
    print(f"Estimated cost of successful runs: ${total_cost:.6f}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=BASE_DIR / "scenarios.csv")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "results.json")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, help="Run only the first N scenarios")
    args = parser.parse_args()
    run_all(args.input, args.output, args.workers, args.limit)
