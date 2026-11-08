import argparse
import json
from pathlib import Path

from pydantic import BaseModel
from typing import Literal
from pydantic_ai import Agent


class JudgeEvaluation(BaseModel):
    reasoning: str
    label: Literal["good", "bad"]


judge_instructions = """You are an expert evaluator assessing a recipe assistant that answers
cooking questions using a fixed recipe collection.

A response is "good" if:
1. It accurately answers using ONLY information from the recipe collection
2. It correctly identifies when a recipe is not available and says so
3. It correctly identifies out-of-scope questions (not about cooking/recipes) and declines

A response is "bad" if ANY of these apply:
1. It makes up recipes, ingredients, or instructions not in the collection (hallucination)
2. It provides cooking advice (substitutions, nutrition info, storage tips) that it
   invented rather than found in the recipe data
3. It answers a question it should have declined (not about recipes, or recipe not available)
4. It gives incorrect information from the recipes (wrong times, wrong ingredients, wrong steps)
5. It says it cannot help when a matching recipe exists in the collection

Be strict about hallucination. The assistant should only provide information it found
in the recipe data. General cooking knowledge that goes beyond the recipe text counts
as hallucination.


Use the supplied tool results as evidence when assessing factual claims.
Accept faithful paraphrases, summaries, and combinations of information
from multiple retrieved recipes.

Do not assume that an ingredient or recipe is absent without checking
the supplied evidence.

Evaluate what the response actually states. A polite offer to continue
helping is not itself invented cooking advice. Penalize it if it makes
an unsupported claim about available recipes or capabilities.

For every bad label, identify a concrete error, unsupported factual claim,
or contradiction and explain how the evidence supports your judgment.

Continue to reject undocumented substitutions, nutrition claims,
and advice that contradicts explicit recipe restrictions.

"""

BASE_DIR = Path(__file__).resolve().parent


def run_judge(input_path=BASE_DIR / "results.json",
              output_path=BASE_DIR / "results_judged_improved.json", evaluator=None):
    if evaluator is None:
        evaluator = Agent(
            'openai:gpt-4o-mini',
            output_type=JudgeEvaluation,
            instructions=judge_instructions,
        )
    results = json.loads(Path(input_path).read_text(encoding="utf-8"))
    if not results:
        raise ValueError("No results to judge")
    if any(row.get("status") == "error" or row.get("output") is None for row in results):
        raise ValueError("Resolve failed agent runs before judging the dataset")

    for i, row in enumerate(results):
        prompt = f"""Question: {row['question']}
Agent response: {row['output']}

Tool calls and results:
{json.dumps(row.get('tools', []), ensure_ascii=False, indent=2)}
"""
        evaluation = evaluator.run_sync(prompt)
        row['judge_label'] = evaluation.output.label
        row['judge_reasoning'] = evaluation.output.reasoning
        print(f"[{i+1}/{len(results)}] {row['judge_label']}: {row['question']}", flush=True)

    Path(output_path).write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    bad = sum(row['judge_label'] == 'bad' for row in results)
    print(f"Saved judged results to {output_path}")
    print(f"Bad: {bad}/{len(results)} ({100 * bad / len(results):.2f}%)")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Judge recipe assistant results")
    parser.add_argument("--input", type=Path, default=BASE_DIR / "results.json")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "results_judged_improved.json")
    args = parser.parse_args()
    run_judge(args.input, args.output)
