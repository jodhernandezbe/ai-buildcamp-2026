from pydantic_ai import Agent

from tools.recipes import get_recipe, search_recipes

INSTRUCTIONS = """You are a recipe assistant. You help users find recipes and answer cooking questions.
1. Use search_recipes to find recipes matching the user's request
2. Use get_recipe to get full details including instructions
3. Answer based on the recipe data you have - do not make up recipes or ingredients
4. If asked about something not in the recipe collection, say you don't have that recipe
5. You can suggest alternatives from the collection if you don't have an exact match
"""


def build_agent() -> Agent:
    return Agent(
        'openai:gpt-4o-mini',
        tools=[search_recipes, get_recipe],
        instructions=INSTRUCTIONS,
    )


if __name__ == '__main__':
    import sys

    question = ' '.join(sys.argv[1:]) or 'How do I make spaghetti carbonara?'
    print(build_agent().run_sync(question).output)
