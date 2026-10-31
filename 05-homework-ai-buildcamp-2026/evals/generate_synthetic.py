import csv
import json

from pydantic import BaseModel
from pydantic_ai import Agent

from evals.paths import DATA_DIR, SYNTHETIC_SCENARIOS_FILE


class Question(BaseModel):
    question: str
    category: str
    type: str


class GeneratedQuestions(BaseModel):
    questions: list[Question]


generator_instructions = """You write realistic questions that users ask a recipe assistant.
Set "category" to the recipe name the question is about.
Set "type" to exactly one of: factual, how-to, detail, substitution, comparison.
"""

generator = Agent(
    'openai:gpt-4o-mini',
    output_type=GeneratedQuestions,
    instructions=generator_instructions,
)

with open(DATA_DIR / 'recipes.json') as f:
    recipes = json.load(f)

rows = []

for i, recipe in enumerate(recipes):
    generation_prompt = f"""Given this recipe, generate 5 questions a user might ask.
Include: 1 factual, 1 how-to, 1 detail, 1 substitution, 1 comparison with another dish.

Recipe: {recipe['name']}
Cuisine: {recipe['cuisine']}
Ingredients: {', '.join(recipe['ingredients'])}
Instructions: {recipe['instructions']}"""

    result = generator.run_sync(generation_prompt)
    questions = result.output.questions

    for q in questions:
        rows.append({'question': q.question, 'category': q.category, 'type': q.type})

    print(f"[{i+1}/{len(recipes)}] {recipe['name']}: {len(questions)} questions")

with open(SYNTHETIC_SCENARIOS_FILE, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['question', 'category', 'type'])
    writer.writeheader()
    writer.writerows(rows)

print(f"\nSaved {len(rows)} questions to {SYNTHETIC_SCENARIOS_FILE}")
