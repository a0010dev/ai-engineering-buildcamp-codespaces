"""Generate five structured evaluation questions for each recipe."""

import argparse
import csv
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from pydantic_ai import Agent

BASE_DIR = Path(__file__).resolve().parent
QUESTION_TYPES = {"factual", "how-to", "detail", "substitution", "comparison"}


class Question(BaseModel):
    question: str = Field(min_length=1)
    category: str = Field(min_length=1)
    type: Literal["factual", "how-to", "detail", "substitution", "comparison"]


class GeneratedQuestions(BaseModel):
    questions: list[Question] = Field(min_length=5, max_length=5)

    @model_validator(mode="after")
    def check_types(self):
        if {q.type for q in self.questions} != QUESTION_TYPES:
            raise ValueError("Include exactly one question of each requested type")
        if len({q.question.strip().casefold() for q in self.questions}) != 5:
            raise ValueError("Questions must be distinct")
        return self


def generate_scenarios(output_path=BASE_DIR / "synthetic_scenarios.csv", generator=None):
    recipes = json.loads((BASE_DIR / "recipes.json").read_text(encoding="utf-8"))
    if generator is None:
        generator = Agent(
            "openai:gpt-4o-mini",
            output_type=GeneratedQuestions,
            instructions="Generate realistic English questions for evaluating a recipe assistant. "
            "Generate questions only, not answers. Follow the requested five types exactly.",
            retries=2,
        )
    questions = []
    for i, recipe in enumerate(recipes, 1):
        others = [r["name"] for r in recipes if r["id"] != recipe["id"]]
        prompt = f"""Given this recipe, generate exactly 5 questions a user might ask.
Include exactly 1 factual, 1 how-to, 1 detail, 1 substitution, and 1 comparison question.
Use those exact values in the type field. Use the recipe name in category.
Every question must name the target dish so it works without conversation history.
For the substitution, ask about replacing an actual ingredient with an alternative;
do not assume the recipe documents whether the substitution works.
For the comparison, name another dish from the list below.
For detail, ask about a relevant time, temperature, serving size, or preparation detail.
Vary the phrasing naturally across recipes.

Recipe data:
{json.dumps(recipe, ensure_ascii=False)}

Other dishes in the collection:
{json.dumps(others, ensure_ascii=False)}"""
        generated = generator.run_sync(prompt).output
        questions.extend(generated.questions)
        print(f"[{i}/{len(recipes)}] Generated 5 questions: {recipe['name']}", flush=True)

    with Path(output_path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "category", "type"])
        writer.writeheader()
        writer.writerows(q.model_dump() for q in questions)
    print(f"Saved {len(questions)} questions to {output_path}")
    return questions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=BASE_DIR / "synthetic_scenarios.csv")
    args = parser.parse_args()
    generate_scenarios(args.output)
