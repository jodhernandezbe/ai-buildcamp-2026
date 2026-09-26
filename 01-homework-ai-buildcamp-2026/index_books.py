import argparse
import json
from pathlib import Path
from typing import Any

from minsearch import Index

BASE_DIR = Path(__file__).resolve().parent
CHUNKS_DIR = BASE_DIR / "data" / "books_chunks"
INDEX_DIR = BASE_DIR / "data" / "index"

BACKENDS = ("markitdown", "pymupdf")
DEFAULT_BACKEND = "pymupdf"

TEXT_FIELDS = ["content"]
KEYWORD_FIELDS = ["source", "title"]


def index_path_for(backend: str, index_dir: Path = INDEX_DIR) -> Path:
    return index_dir / f"{backend}.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a search index from chunked book text")
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        default=DEFAULT_BACKEND,
        help=f"Which chunks to index (default: {DEFAULT_BACKEND})",
    )
    parser.add_argument(
        "--chunks-dir",
        type=Path,
        default=CHUNKS_DIR,
        help=f"Base directory with chunks, one subfolder per backend (default: {CHUNKS_DIR})",
    )
    parser.add_argument(
        "--index-dir",
        type=Path,
        default=INDEX_DIR,
        help=f"Directory to save the index to, one file per backend (default: {INDEX_DIR})",
    )
    return parser.parse_args()


def load_chunks(chunks_dir: Path = CHUNKS_DIR, backend: str = DEFAULT_BACKEND) -> list[dict[str, Any]]:
    chunks = []

    for chunks_path in sorted((chunks_dir / backend).glob("*.json")):
        chunks.extend(json.loads(chunks_path.read_text(encoding="utf-8")))

    return chunks


def prepare_documents(
        chunks: list[dict[str, Any]],
        ) -> list[dict[str, Any]]:
    documents = []

    for chunk in chunks:
        document = chunk.copy()
        document["content"] = "\n".join(document["content"])
        documents.append(document)

    return documents


def index_books(
        chunks_dir: Path = CHUNKS_DIR,
        backend: str = DEFAULT_BACKEND,
        ) -> Index:
    chunks = load_chunks(chunks_dir, backend)
    documents = prepare_documents(chunks)

    index = Index(
        text_fields=TEXT_FIELDS,
        keyword_fields=KEYWORD_FIELDS,
        )
    index.fit(documents)

    return index


def main() -> None:
    args = parse_args()
    index = index_books(args.chunks_dir, args.backend)

    index_path = index_path_for(args.backend, args.index_dir)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index.save(index_path)
    print(f"Indexed {len(index.docs)} chunks [{args.backend}] -> {index_path}")


if __name__ == "__main__":
    main()
