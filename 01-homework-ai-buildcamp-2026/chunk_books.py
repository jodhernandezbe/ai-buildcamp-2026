import argparse
import csv
import json
from pathlib import Path
from typing import Any

from gitsource import chunk_documents

from download_books import CSV_PATH, slugify

BASE_DIR = Path(__file__).resolve().parent
TEXT_DIR = BASE_DIR / "data" / "books_text"
CHUNKS_DIR = BASE_DIR / "data" / "books_chunks"

BACKENDS = ("markitdown", "pymupdf")
DEFAULT_BACKEND = "pymupdf"

CHUNK_SIZE = 100
CHUNK_STEP = 50


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Split extracted book text into overlapping chunks")
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        default=DEFAULT_BACKEND,
        help=f"Which converted text to chunk (default: {DEFAULT_BACKEND})",
    )
    parser.add_argument(
        "--text-dir",
        type=Path,
        default=TEXT_DIR,
        help=f"Base directory with converted text, one subfolder per backend (default: {TEXT_DIR})",
    )
    parser.add_argument(
        "--chunks-dir",
        type=Path,
        default=CHUNKS_DIR,
        help=f"Base directory for chunk output, one subfolder per backend (default: {CHUNKS_DIR})",
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=CHUNK_SIZE,
        help=f"Number of lines per chunk (default: {CHUNK_SIZE})",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=CHUNK_STEP,
        help=f"Number of lines to move forward per chunk (default: {CHUNK_STEP})",
    )
    return parser.parse_args()


def build_title_map(csv_path: Path = CSV_PATH) -> dict[str, str]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {
            slugify(row["title"].strip()): row["title"].strip()
            for row in reader
            if row.get("title", "").strip()
        }


def read_documents(
        text_dir: Path = TEXT_DIR,
        backend: str = DEFAULT_BACKEND,
        csv_path: Path = CSV_PATH,
        ) -> list[dict[str, Any]]:
    title_map = build_title_map(csv_path)
    documents = []

    for md_path in sorted((text_dir / backend).glob("*.md")):
        lines = md_path.read_text(encoding="utf-8").split("\n")
        content = [line for line in lines if line.strip()]
        title = title_map.get(md_path.stem, md_path.stem)
        documents.append({"source": md_path.name, "title": title, "content": content})

    return documents


def chunk_books(
        text_dir: Path = TEXT_DIR,
        chunks_dir: Path = CHUNKS_DIR,
        backend: str = DEFAULT_BACKEND,
        size: int = CHUNK_SIZE,
        step: int = CHUNK_STEP,
        ) -> dict[str, list[dict[str, Any]]]:
    backend_chunks_dir = chunks_dir / backend
    backend_chunks_dir.mkdir(parents=True, exist_ok=True)
    documents = read_documents(text_dir, backend)
    chunks_by_book = {}

    for document in documents:
        chunks = chunk_documents([document], size=size, step=step)
        chunks_by_book[document["source"]] = chunks

        dest = backend_chunks_dir / f"{Path(document['source']).stem}.json"
        dest.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
        print(f"[{backend}] {document['source']} -> {len(chunks)} chunks -> {dest.relative_to(chunks_dir)}")

    return chunks_by_book


def main() -> None:
    args = parse_args()
    chunks_by_book = chunk_books(args.text_dir, args.chunks_dir, args.backend, args.size, args.step)
    total = sum(len(chunks) for chunks in chunks_by_book.values())
    print(f"Created {total} chunks from {len(chunks_by_book)} books -> {args.chunks_dir / args.backend}")


if __name__ == "__main__":
    main()
