import json
import sys

from pydantic import BaseModel
from typing import Literal
from pydantic_ai import Agent

from evals.paths import DATA_DIR, JUDGED_FILE, RESULTS_FILE


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

The full recipe collection is given below. Check every factual claim in the response
against it instead of guessing:
- Recipe names, cuisines, times, servings, ingredients, tags, and steps that match the
  collection are correct. Do not mark a response bad for "not confirming" that a recipe
  exists when it does exist in the collection.
- Details that are absent from the collection are invented, even when they sound
  plausible. This includes quantities and measurements, extra steps, cooking tips, and
  nutrition facts.
- Rewording or reformatting recipe text, or converting units of a stated value
  (for example, a temperature), does not add new facts.

These behaviors are acceptable and do not make a response bad on their own:
- Asking a short clarifying question when the request is too vague to pick a recipe,
  as long as the response invents nothing.
- After correctly saying a recipe is not in the collection, offering to suggest
  alternatives from the collection.

A response that says a recipe is not available and then explains how to make it anyway
from general knowledge is bad.
"""

with open(DATA_DIR / 'recipes.json') as f:
    recipes = json.load(f)

judge_instructions += "\nRecipe collection:\n" + json.dumps(recipes, indent=1)

judge_agent = Agent(
    'openai:gpt-4o-mini',
    output_type=JudgeEvaluation,
    instructions=judge_instructions,
)

# Usage: python -m evals.judge [results.json] [results_judged.json]
results_file = sys.argv[1] if len(sys.argv) > 1 else RESULTS_FILE
judged_file = sys.argv[2] if len(sys.argv) > 2 else JUDGED_FILE

with open(results_file) as f:
    results = json.load(f)

for i, row in enumerate(results):
    prompt = f"""Question: {row['question']}
Agent response: {row['output']}"""

    evaluation = judge_agent.run_sync(prompt)
    row['judge_label'] = evaluation.output.label
    row['judge_reasoning'] = evaluation.output.reasoning
    print(f"[{i+1}/{len(results)}] {row['judge_label']}: {row['question']}")

with open(judged_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved judged results to {judged_file}")
