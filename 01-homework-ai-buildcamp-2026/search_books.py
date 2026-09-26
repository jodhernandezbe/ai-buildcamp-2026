import argparse
from pathlib import Path

from minsearch import Index

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "data" / "index.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search the indexed book chunks")
    parser.add_argument("query", help="Text to search for")
    parser.add_argument(
        "-n", "--num-results",
        type=int,
        default=5,
        help="Number of results to return (default: 5)",
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        default=INDEX_PATH,
        help=f"Path to the saved index (default: {INDEX_PATH})",
    )
    return parser.parse_args()


def search_books(
        query: str,
        num_results: int = 5,
        index_path: Path = INDEX_PATH,
        ) -> list[dict]:
    index = Index.load(index_path)
    return index.search(query, num_results=num_results)


def main() -> None:
    args = parse_args()
    results = search_books(args.query, args.num_results, args.index_path)

    if not results:
        print("No results found.")
        return

    for rank, result in enumerate(results, start=1):
        print(f"#{rank} | {result['title']}")


if __name__ == "__main__":
    main()
