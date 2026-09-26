import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "data" / "books_pdf"
TEXT_DIR = BASE_DIR / "data" / "books_text"

BACKENDS = ("markitdown", "pymupdf")
DEFAULT_BACKEND = "pymupdf"


def convert_with_markitdown(pdf_path: Path) -> str:
    from markitdown import MarkItDown
    converter = MarkItDown()
    return converter.convert(pdf_path).text_content


def convert_with_pymupdf(pdf_path: Path) -> str:
    import pymupdf
    with pymupdf.open(pdf_path) as doc:
        return "\n".join(page.get_text() for page in doc)


CONVERTERS = {
    "markitdown": convert_with_markitdown,
    "pymupdf": convert_with_pymupdf,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert book PDFs to plain text")
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        default=DEFAULT_BACKEND,
        help=f"PDF text extraction backend to use (default: {DEFAULT_BACKEND})",
    )
    parser.add_argument(
        "--pdf-dir",
        type=Path,
        default=PDF_DIR,
        help=f"Directory with the PDF files (default: {PDF_DIR})",
    )
    parser.add_argument(
        "--text-dir",
        type=Path,
        default=TEXT_DIR,
        help=f"Base directory for extracted text, one subfolder per backend (default: {TEXT_DIR})",
    )
    return parser.parse_args()


def convert_books(
        pdf_dir: Path = PDF_DIR,
        text_dir: Path = TEXT_DIR,
        backend: str = DEFAULT_BACKEND,
        ) -> list[Path]:
    backend_dir = text_dir / backend
    backend_dir.mkdir(parents=True, exist_ok=True)
    convert = CONVERTERS[backend]
    converted = []

    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        dest = backend_dir / f"{pdf_path.stem}.md"
        if dest.exists():
            print(f"Skipping (already exists): {dest.relative_to(text_dir)}")
            converted.append(dest)
            continue

        print(f"Converting [{backend}] {pdf_path.name} -> {dest.relative_to(text_dir)}")
        text = convert(pdf_path)
        dest.write_text(text, encoding="utf-8")
        converted.append(dest)

    return converted


def main() -> None:
    args = parse_args()
    convert_books(args.pdf_dir, args.text_dir, args.backend)


if __name__ == "__main__":
    main()
