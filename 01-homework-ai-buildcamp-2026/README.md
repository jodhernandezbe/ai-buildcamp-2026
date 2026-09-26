# Week 1 Homework: AI Engineering Buildcamp - From RAG to Agents

This folder contains the homework for the first week of the course. The goal is to
build the document preparation part of a RAG (Retrieval-Augmented Generation)
pipeline: take a set of programming books in PDF form, turn them into searchable
text, and build a simple search index over them.

## Structure

```
01-homework-ai-buildcamp-2026/
  data/
    books.csv          list of books with title, book page, and pdf link
    books_pdf/         downloaded PDF files
    books_text/        PDFs converted to plain text (one .md file per book)
    books_chunks/       text split into overlapping chunks (one .json file per book)
    index.json         the search index built from the chunks
  download_books.py
  convert_books.py
  chunk_books.py
  index_books.py
  search_books.py
  rag.py
  prepare_rag_documents.py
```

Each stage reads the output of the previous one, and each script can be run on
its own or through `prepare_rag_documents.py`, which runs all of them in order.

## What each script does

**download_books.py**
Reads `books.csv` and downloads each book's PDF into `data/books_pdf/`. Skips a
book if its PDF is already there.

**convert_books.py**
Converts each PDF into plain text using PyMuPDF, and saves it as a `.md` file in
`data/books_text/`. Skips a book if the text file already exists.

**chunk_books.py**
Reads each text file, splits it into lines, and removes empty or blank lines.
Then it splits each book into overlapping chunks (100 lines per chunk, moving
forward 50 lines at a time) using the `chunk_documents` function from the
`gitsource` package. Each chunk keeps the book title and source filename, and is
saved to `data/books_chunks/` as one JSON file per book.

**index_books.py**
Loads all the chunk files and builds a search index with `minsearch`. The chunk
content is used as searchable text, while the title and source filename are kept
as fields you can filter or boost on. The index is saved to `data/index.json`.

**prepare_rag_documents.py**
Runs all four steps above in order: download, convert, chunk, index. Use this
when setting up the pipeline from scratch.

**search_books.py**
A command line tool to query the index. You pass in a search text and, if you
want, the number of results to show. It prints the matching books, ranked from
the best match to the weakest.

Usage:
```
python search_books.py "your search text" [-n NUM_RESULTS] [--index-path PATH]
```

- `query` (required): the text to search for.
- `-n, --num-results` (optional, default 5): how many results to print.
- `--index-path` (optional, default `data/index.json`): index file to search.

Example:
```
python search_books.py "how does recursion work in python" -n 3
```

**rag.py**
A command line tool that answers a question using RAG. It searches the index
for matching chunks, builds a prompt with the question and the matched
content, and sends it to an LLM to get an answer. It also reports how many
input and output tokens the call used, so you can see the cost of each
question. Pass `--structured` to get the answer as a structured `RAGResponse`
object (with a confidence score, an answer type, and follow-up questions)
instead of plain text.

Usage:
```
python rag.py "your question" [-n NUM_RESULTS] [--index-path PATH] [--model MODEL] [--structured]
```

- `query` (required): the question to ask.
- `-n, --num-results` (optional, default 5): how many chunks to use as context.
- `--index-path` (optional, default `data/index.json`): index file to search.
- `--model` (optional, default `gpt-4o-mini`): OpenAI model to use.
- `--structured` (optional flag, off by default): return a structured
  `RAGResponse` object instead of plain text.

Example:
```
python rag.py "python function definition"
python rag.py "python function definition" --structured
```

## Why PyMuPDF instead of markitdown

The first version of `convert_books.py` used the `markitdown` package to turn
PDFs into text. This worked fine for most books, but one PDF, Think Python,
had a problem: many words in the extracted text were missing the space between
them, for example "Squareroots" instead of "Square roots". This is not a bug in
our code. It comes from how that specific PDF stores its text, and it also
happened when testing with `pdfplumber`, a different extraction library.

This mattered because our search relies on matching words. If a book's text is
full of joined-up words, normal search terms will not match its content well,
and the book will barely show up in results, even when it is the most relevant
one.

We tested PyMuPDF on the same PDF and it extracted the text with the spaces in
the right place. So we switched to it for all books to keep the pipeline
consistent, and the search results improved right away for Think Python.
