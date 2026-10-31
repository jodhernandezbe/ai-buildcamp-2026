# Homework 5 (Week 6): AI Engineering Buildcamp - Evaluating a Recipe Agent

This folder contains the fifth homework. The goal is to evaluate a recipe assistant
that answers cooking questions from a fixed collection of 15 recipes: write test
scenarios, label the agent's answers by hand, build an LLM judge, measure how well
the judge agrees with the human labels, improve the judge prompt, and scale up with
synthetic questions. It uses PydanticAI as the framework and OpenAI (`gpt-4o-mini`)
as the provider.

## Structure

```
05-homework-ai-buildcamp-2026/
  data/
    recipes.json             the 15-recipe collection
    scenarios.csv            20 hand-written scenarios: question, category, type
    synthetic_scenarios.csv  75 LLM-generated questions (5 per recipe)
    labels.csv               human labels for results.json: good/bad and failure reason
    labels_before_regrade.csv  labels before two stale grades were corrected
    results/
      results.json           agent answers to scenarios.csv
      results_judged.json    judge labels for results.json (updated judge prompt)
      results_judged_v1.json judge labels from the original judge prompt
      synthetic_results.json         agent answers to synthetic_scenarios.csv
      synthetic_results_judged.json  judge labels for the synthetic answers
  tools/
    recipes/
      recipe_tools.py        minsearch index: search_recipes(query) and get_recipe(id)
  agent/
    agent.py                 build_agent(): model, instructions, tools
  evals/
    paths.py                 locations of the data and result files
    run_scenarios.py         runs the agent on a scenarios CSV, records tokens and cost
    label_results.py         interactive good/bad labeling with a failure reason
    judge.py                 LLM judge: labels each answer good or bad, with reasoning
    compare_judge.py         judge vs. human labels: TP/FP/FN/TN, accuracy, precision, recall
    generate_synthetic.py    generates 5 questions per recipe with structured output
```

## Design notes

- **The judge sees the recipe collection.** The original judge only saw the question
  and the answer, so it guessed what was real. It flagged correct answers as
  unverified and missed invented quantities. The updated prompt includes the full
  collection and general rules for clarifying questions, offering alternatives, and
  details that sound plausible but aren't in the data.
- **Labels describe specific answers.** The agent's wording changes between runs, so
  `labels.csv` stores the answer that was labeled. Relabel after rerunning the agent.
- **Failure reasons** are one of `hallucination`, `wrong-scope`, `incomplete`, or
  `incorrect-details`.
- **Synthetic questions are labeled by type.** Each one is `factual`, `how-to`,
  `detail`, `substitution`, or `comparison`, with the recipe name as its category.

## Results

| Measure | Value |
|---------|-------|
| Hand-written scenarios labeled bad (human) | 12 of 20 |
| Judge disagreements before / after the prompt change | 4 / 0 |
| Judge accuracy, precision, recall after the change | 1.00, 1.00, 1.00 |
| Synthetic questions labeled bad (judge) | 61 of 75 (81.3%) |

The prompt was tuned on the same 20 scenarios it is scored on, so the 1.00 scores
are optimistic. The synthetic labels were not checked by hand.

## Usage

Requires `OPENAI_API_KEY` in the environment. Run everything from this folder with
`python -m`, so this folder is on the import path.

Ask the agent a question:
```
python -m agent.agent "How do I make spaghetti carbonara?"
```

Run the agent on the scenarios, then judge the answers:
```
python -m evals.run_scenarios
python -m evals.judge
```

Label the answers by hand (skips questions already in `data/labels.csv`), then
compare with the judge:
```
python -m evals.label_results
python -m evals.compare_judge
```

Generate synthetic questions, then run and judge them with explicit file paths:
```
python -m evals.generate_synthetic
python -m evals.run_scenarios data/synthetic_scenarios.csv data/results/synthetic_results.json
python -m evals.judge data/results/synthetic_results.json data/results/synthetic_results_judged.json
```

A full run of the 20 scenarios costs about $0.003, and the 75 synthetic questions
about $0.011, plus the judge calls. Answers and labels can differ slightly from run
to run.
