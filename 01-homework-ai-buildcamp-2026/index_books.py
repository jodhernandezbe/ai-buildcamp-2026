import json
from pathlib import Path
from typing import Any

from minsearch import Index

BASE_DIR = Path(__file__).resolve().parent
CHUNKS_DIR = BASE_DIR / "data" / "books_chunks"
INDEX_PATH = BASE_DIR / "data" / "index.json"

TEXT_FIELDS = ["content"]
KEYWORD_FIELDS = ["source", "title"]


def load_chunks(
        chunks_dir: Path = CHUNKS_DIR,
        ) -> list[dict[str, Any]]:
    chunks = []

    for chunks_path in sorted(chunks_dir.glob("*.json")):
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
        ) -> Index:
    chunks = load_chunks(chunks_dir)
    documents = prepare_documents(chunks)

    index = Index(
        text_fields=TEXT_FIELDS,
        keyword_fields=KEYWORD_FIELDS,
        )
    index.fit(documents)

    return index


if __name__ == "__main__":
    index = index_books()
    index.save(INDEX_PATH)
    print(f"Indexed {len(index.docs)} chunks -> {INDEX_PATH}")
