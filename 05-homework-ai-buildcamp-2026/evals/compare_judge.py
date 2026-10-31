import csv
import json

from evals.paths import JUDGED_FILE, LABELS_FILE


def load_judge_labels():
    with open(JUDGED_FILE) as f:
        return {row['question']: row['judge_label'] for row in json.load(f)}


def load_human_labels():
    with open(LABELS_FILE, newline='') as f:
        return {row['question']: row['label'] for row in csv.DictReader(f)}


def confusion_counts(judge, human):
    counts = {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}
    for question in judge:
        judge_bad = judge[question] == 'bad'
        human_bad = human[question] == 'bad'

        if judge_bad and human_bad:
            counts['tp'] += 1
        elif judge_bad:
            counts['fp'] += 1
            print(f"FP: {question}")
        elif human_bad:
            counts['fn'] += 1
            print(f"FN: {question}")
        else:
            counts['tn'] += 1
    return counts


def main():
    judge = load_judge_labels()
    human = load_human_labels()

    if judge.keys() != human.keys():
        missing = judge.keys() ^ human.keys()
        raise SystemExit(f"Question mismatch between files: {sorted(missing)}")

    c = confusion_counts(judge, human)
    tp, fp, fn, tn = c['tp'], c['fp'], c['fn'], c['tn']
    total = tp + fp + fn + tn

    print(f"\nTP={tp} FP={fp} FN={fn} TN={tn} total={total}")
    print(f"accuracy  = {(tp + tn) / total:.2f}")
    print(f"precision = {tp / (tp + fp):.2f}" if tp + fp else "precision = n/a (judge never said bad)")
    print(f"recall    = {tp / (tp + fn):.2f}" if tp + fn else "recall    = n/a (no human bad labels)")


if __name__ == '__main__':
    main()
