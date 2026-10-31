from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
RESULTS_DIR = DATA_DIR / 'results'

SCENARIOS_FILE = DATA_DIR / 'scenarios.csv'
SYNTHETIC_SCENARIOS_FILE = DATA_DIR / 'synthetic_scenarios.csv'
LABELS_FILE = DATA_DIR / 'labels.csv'
RESULTS_FILE = RESULTS_DIR / 'results.json'
JUDGED_FILE = RESULTS_DIR / 'results_judged.json'
