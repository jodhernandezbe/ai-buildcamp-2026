import argparse

from download_books import download_books
from convert_books import BACKENDS, DEFAULT_BACKEND, convert_books
from chunk_books import chunk_books
from index_books import index_path_for, index_books


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full RAG document preparation pipeline")
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        default=DEFAULT_BACKEND,
        help=f"PDF text extraction backend to use for convert/chunk/index (default: {DEFAULT_BACKEND})",
    )
    return parser.parse_args()


def prepare_rag_documents(backend: str = DEFAULT_BACKEND) -> None:
    print("Step 1/4: downloading books")
    download_books()

    print(f"Step 2/4: converting PDFs to markdown [{backend}]")
    convert_books(backend=backend)

    print(f"Step 3/4: chunking books [{backend}]")
    chunks_by_book = chunk_books(backend=backend)
    total_chunks = sum(len(chunks) for chunks in chunks_by_book.values())
    print(f"Created {total_chunks} chunks from {len(chunks_by_book)} books")

    print(f"Step 4/4: indexing chunks [{backend}]")
    index = index_books(backend=backend)
    index_path = index_path_for(backend)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index.save(index_path)
    print(f"Indexed {len(index.docs)} chunks -> {index_path}")


if __name__ == "__main__":
    args = parse_args()
    prepare_rag_documents(args.backend)
