from collections import defaultdict

from pydantic_ai import RunUsage


# USD per milió de tokens.
MODEL_PRICES = {
    "openai:gpt-4o-mini": {
        "input": 0.15,
        "cached_input": 0.075,
        "output": 0.60,
    },
}

usage_by_model = defaultdict(RunUsage)


def reset_usage():
    usage_by_model.clear()


def capture_usage(model_name, usage):
    usage_by_model[model_name] += usage


def calculate_cost(model_name, usage):
    prices = MODEL_PRICES[model_name]

    cached_tokens = usage.cache_read_tokens
    normal_tokens = usage.input_tokens - cached_tokens

    return (
        normal_tokens * prices["input"]
        + cached_tokens * prices["cached_input"]
        + usage.output_tokens * prices["output"]
    ) / 1_000_000


def display_total_usage():
    total_cost = 0.0

    print("\nCost tracking:")

    for model_name, usage in usage_by_model.items():
        cost = calculate_cost(model_name, usage)
        total_cost += cost

        print(
            f"{model_name}: "
            f"input={usage.input_tokens}, "
            f"cached={usage.cache_read_tokens}, "
            f"output={usage.output_tokens}, "
            f"cost=${cost:.6f}"
        )

    print(f"Total cost: ${total_cost:.6f}")
