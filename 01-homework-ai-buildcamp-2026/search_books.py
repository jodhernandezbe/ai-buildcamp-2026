import argparse
from pathlib import Path

from minsearch import Index

from index_books import BACKENDS, DEFAULT_BACKEND, index_path_for


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
        "--backend",
        choices=BACKENDS,
        default=DEFAULT_BACKEND,
        help=f"Which index to search, by the backend used to build it (default: {DEFAULT_BACKEND})",
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        default=None,
        help="Path to a specific index file (overrides --backend)",
    )
    return parser.parse_args()


def search_books(
        query: str,
        num_results: int = 5,
        backend: str = DEFAULT_BACKEND,
        index_path: Path | None = None,
        ) -> list[dict]:
    index_path = index_path or index_path_for(backend)
    index = Index.load(index_path)
    return index.search(query, num_results=num_results)


def main() -> None:
    args = parse_args()
    results = search_books(args.query, args.num_results, args.backend, args.index_path)

    if not results:
        print("No results found.")
        return

    for rank, result in enumerate(results, start=1):
        print(f"#{rank} | {result['title']}")


if __name__ == "__main__":
    main()
