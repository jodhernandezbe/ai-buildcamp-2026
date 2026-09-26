import csv
import json
from pathlib import Path
from typing import Any

from gitsource import chunk_documents

from download_books import CSV_PATH, slugify

BASE_DIR = Path(__file__).resolve().parent
TEXT_DIR = BASE_DIR / "data" / "books_text"
CHUNKS_DIR = BASE_DIR / "data" / "books_chunks"

CHUNK_SIZE = 100
CHUNK_STEP = 50


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
        csv_path: Path = CSV_PATH,
        ) -> list[dict[str, Any]]:
    title_map = build_title_map(csv_path)
    documents = []

    for md_path in sorted(text_dir.glob("*.md")):
        lines = md_path.read_text(encoding="utf-8").split("\n")
        content = [line for line in lines if line.strip()]
        title = title_map.get(md_path.stem, md_path.stem)
        documents.append({"source": md_path.name, "title": title, "content": content})

    return documents


def chunk_books(
        text_dir: Path = TEXT_DIR,
        chunks_dir: Path = CHUNKS_DIR,
        size: int = CHUNK_SIZE,
        step: int = CHUNK_STEP,
        ) -> dict[str, list[dict[str, Any]]]:
    chunks_dir.mkdir(parents=True, exist_ok=True)
    documents = read_documents(text_dir)
    chunks_by_book = {}

    for document in documents:
        chunks = chunk_documents([document], size=size, step=step)
        chunks_by_book[document["source"]] = chunks

        dest = chunks_dir / f"{Path(document['source']).stem}.json"
        dest.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
        print(f"{document['source']} -> {len(chunks)} chunks -> {dest.name}")

    return chunks_by_book


if __name__ == "__main__":
    chunks_by_book = chunk_books()
    total = sum(len(chunks) for chunks in chunks_by_book.values())
    print(f"Created {total} chunks from {len(chunks_by_book)} books -> {CHUNKS_DIR}")
