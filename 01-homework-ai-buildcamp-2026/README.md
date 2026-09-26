# Week 1 Homework: AI Engineering Buildcamp - From RAG to Agents

This folder contains the homework for the first week of the course. The goal is to
build the document preparation part of a RAG (Retrieval-Augmented Generation)
pipeline: take a set of programming books in PDF form, turn them into searchable
text, and build a simple search index over them.

## Structure

```
01-homework-ai-buildcamp-2026/
  data/
    books.csv              list of books with title, book page, and pdf link
    books_pdf/             downloaded PDF files
    books_text/
      markitdown/          PDFs converted to plain text using markitdown
      pymupdf/             PDFs converted to plain text using PyMuPDF
    books_chunks/
      markitdown/          markitdown text split into overlapping chunks
      pymupdf/             PyMuPDF text split into overlapping chunks
    index/
      markitdown.json      search index built from the markitdown chunks
      pymupdf.json         search index built from the PyMuPDF chunks
  download_books.py
  convert_books.py
  chunk_books.py
  index_books.py
  search_books.py
  rag.py
  prepare_rag_documents.py
```

The PDFs can be turned into text with two different backends: `markitdown` or
`pymupdf`. Each backend keeps its own text, chunks, and index side by side, so
you can build and compare both without one overwriting the other. Every
script that deals with text, chunks, or the index takes a `--backend` flag to
choose which one to use. `pymupdf` is the default (see below for why).

Each stage reads the output of the previous one, and each script can be run on
its own or through `prepare_rag_documents.py`, which runs all of them in order.

## What each script does

**download_books.py**
Reads `books.csv` and downloads each book's PDF into `data/books_pdf/`. Skips a
book if its PDF is already there.

**convert_books.py**
Converts each PDF into plain text, and saves it as a `.md` file in
`data/books_text/<backend>/`. Skips a book if the text file already exists.

Usage:
```
python convert_books.py [--backend markitdown|pymupdf]
```

**chunk_books.py**
Reads each text file for the chosen backend, splits it into lines, and removes
empty or blank lines. Then it splits each book into overlapping chunks (100
lines per chunk, moving forward 50 lines at a time by default) using the
`chunk_documents` function from the `gitsource` package. Each chunk keeps the
book title and source filename, and is saved to `data/books_chunks/<backend>/`
as one JSON file per book.

Usage:
```
python chunk_books.py [--backend markitdown|pymupdf] [-s SIZE] [--step STEP]
```

**index_books.py**
Loads all the chunk files for the chosen backend and builds a search index
with `minsearch`. The chunk content is used as searchable text, while the
title and source filename are kept as fields you can filter or boost on. The
index is saved to `data/index/<backend>.json`.

Usage:
```
python index_books.py [--backend markitdown|pymupdf]
```

**prepare_rag_documents.py**
Runs all four steps above in order: download, convert, chunk, index, for the
chosen backend. Use this when setting up the pipeline from scratch.

Usage:
```
python prepare_rag_documents.py [--backend markitdown|pymupdf]
```

**search_books.py**
A command line tool to query an index. You pass in a search text and, if you
want, the number of results to show and which backend's index to use. It
prints the matching books, ranked from the best match to the weakest.

Usage:
```
python search_books.py "your search text" [-n NUM_RESULTS] [--backend markitdown|pymupdf] [--index-path PATH]
```

- `query` (required): the text to search for.
- `-n, --num-results` (optional, default 5): how many results to print.
- `--backend` (optional, default `pymupdf`): which index to search.
- `--index-path` (optional): a specific index file, overrides `--backend`.

Example:
```
python search_books.py "how does recursion work in python" -n 3
python search_books.py "how does recursion work in python" --backend markitdown
```

**rag.py**
A command line tool that answers a question using RAG. It searches an index
for matching chunks, builds a prompt with the question and the matched
content, and sends it to an LLM to get an answer. It also reports how many
input and output tokens the call used, so you can see the cost of each
question. Pass `--structured` to get the answer as a structured `RAGResponse`
object (with a confidence score, an answer type, and follow-up questions)
instead of plain text.

Usage:
```
python rag.py "your question" [-n NUM_RESULTS] [--backend markitdown|pymupdf] [--index-path PATH] [--model MODEL] [--structured]
```

- `query` (required): the question to ask.
- `-n, --num-results` (optional, default 5): how many chunks to use as context.
- `--backend` (optional, default `pymupdf`): which index to use.
- `--index-path` (optional): a specific index file, overrides `--backend`.
- `--model` (optional, default `gpt-4o-mini`): OpenAI model to use.
- `--structured` (optional flag, off by default): return a structured
  `RAGResponse` object instead of plain text.

Example:
```
python rag.py "python function definition"
python rag.py "python function definition" --backend markitdown
python rag.py "python function definition" --structured
```

## Why PyMuPDF is the default

The first version of `convert_books.py` only used the `markitdown` package to
turn PDFs into text. This worked fine for most books, but one PDF, Think
Python, had a problem: many words in the extracted text were missing the
space between them, for example "Squareroots" instead of "Square roots". This
comes from how that specific PDF stores its text, and it also happened when
testing with `pdfplumber`, a different extraction library.

This mattered because search relies on matching words. If a book's text is
full of joined-up words, normal search terms will not match its content well,
and the book will barely show up in results, even when it is the most
relevant one. For example, searching "python function definition" against the
markitdown index puts Physical Modeling in MATLAB first and Think Python
third, while the same search against the PyMuPDF index correctly puts Think
Python first.

I tested PyMuPDF on the same PDF and it extracted the text with the spaces in
the right place, so it became the default backend. Both backends are kept in
the repository so the difference can still be reproduced and compared.
