import csv
import json
import os

from evals.paths import LABELS_FILE, RESULTS_FILE

FIELDS = ['question', 'category', 'type', 'output', 'label', 'reason']
REASONS = ['hallucination', 'wrong-scope', 'incomplete', 'incorrect-details']


def load_existing_labels():
    if not os.path.exists(LABELS_FILE):
        return []
    with open(LABELS_FILE, newline='') as f:
        return list(csv.DictReader(f))


def save_labels(rows):
    with open(LABELS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def ask_label():
    while True:
        answer = input("Label (good/bad, q to quit): ").strip().lower()
        if answer in ('good', 'bad', 'q'):
            return answer
        print("Please enter 'good', 'bad', or 'q'.")


def ask_reason():
    options = ', '.join(REASONS)
    while True:
        answer = input(f"Why it failed ({options}): ").strip().lower()
        if answer in REASONS:
            return answer
        print(f"Please enter one of: {options}.")


def main():
    with open(RESULTS_FILE) as f:
        results = json.load(f)

    labels = load_existing_labels()
    done = {row['question'] for row in labels}

    for i, result in enumerate(results):
        if result['question'] in done:
            continue

        print(f"\n[{i+1}/{len(results)}] {result['category']} / {result['type']}")
        print(f"Question: {result['question']}")
        print(f"Response: {result['output']}\n")

        label = ask_label()
        if label == 'q':
            break

        reason = ask_reason() if label == 'bad' else ''

        labels.append({
            'question': result['question'],
            'category': result['category'],
            'type': result['type'],
            'output': result['output'],
            'label': label,
            'reason': reason,
        })
        # Save after every label so progress survives an interrupt.
        save_labels(labels)

    print(f"\nSaved {len(labels)} labels to {LABELS_FILE}")


if __name__ == '__main__':
    main()
