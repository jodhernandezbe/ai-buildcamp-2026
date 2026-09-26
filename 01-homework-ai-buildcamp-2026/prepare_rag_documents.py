from download_books import download_books
from convert_books import convert_books
from chunk_books import chunk_books
from index_books import INDEX_PATH, index_books


def prepare_rag_documents() -> None:
    print("Step 1/4: downloading books")
    download_books()

    print("Step 2/4: converting PDFs to markdown")
    convert_books()

    print("Step 3/4: chunking books")
    chunks_by_book = chunk_books()
    total_chunks = sum(len(chunks) for chunks in chunks_by_book.values())
    print(f"Created {total_chunks} chunks from {len(chunks_by_book)} books")

    print("Step 4/4: indexing chunks")
    index = index_books()
    index.save(INDEX_PATH)
    print(f"Indexed {len(index.docs)} chunks -> {INDEX_PATH}")


if __name__ == "__main__":
    prepare_rag_documents()
