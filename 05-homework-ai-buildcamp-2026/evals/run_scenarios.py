import csv
import json
import sys
import time

from agent import build_agent
from evals.paths import RESULTS_FILE, SCENARIOS_FILE

agent = build_agent()

MODEL_PRICES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


def calculate_cost(usage, model="gpt-4o-mini"):
    prices = MODEL_PRICES[model]
    input_cost = (usage.input_tokens / 1_000_000) * prices["input"]
    output_cost = (usage.output_tokens / 1_000_000) * prices["output"]
    return round(input_cost + output_cost, 6)


def run_all(scenarios_file=SCENARIOS_FILE, results_file=RESULTS_FILE):
    with open(scenarios_file) as f:
        scenarios = list(csv.DictReader(f))

    results = []

    for i, scenario in enumerate(scenarios):
        question = scenario['question']
        print(f"[{i+1}/{len(scenarios)}] {question}")

        start = time.time()
        result = agent.run_sync(question)
        elapsed = time.time() - start

        usage = result.usage
        cost = calculate_cost(usage)

        results.append({
            'question': question,
            'category': scenario['category'],
            'type': scenario['type'],
            'output': result.output,
            'execution_time': round(elapsed, 2),
            'tokens': {
                'input_tokens': usage.input_tokens,
                'output_tokens': usage.output_tokens,
                'total_tokens': usage.total_tokens,
            },
            'cost': cost,
        })

        print(f"  Done in {elapsed:.1f}s (${cost})")

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    total_cost = sum(r['cost'] for r in results)
    print(f"\nSaved {len(results)} results to {results_file}")
    print(f"Total cost: ${total_cost:.4f}")

if __name__ == "__main__":
    # Usage: python -m evals.run_scenarios [scenarios.csv] [results.json]
    run_all(*sys.argv[1:3])
