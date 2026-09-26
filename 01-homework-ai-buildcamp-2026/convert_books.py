from pathlib import Path

import pymupdf

BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "data" / "books_pdf"
TEXT_DIR = BASE_DIR / "data" / "books_text"


def convert_books(
        pdf_dir: Path = PDF_DIR,
        text_dir: Path = TEXT_DIR,
        ) -> list[Path]:
    text_dir.mkdir(parents=True, exist_ok=True)
    converted = []

    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        dest = text_dir / f"{pdf_path.stem}.md"
        if dest.exists():
            print(f"Skipping (already exists): {dest.name}")
            converted.append(dest)
            continue

        print(f"Converting {pdf_path.name} -> {dest.name}")
        with pymupdf.open(pdf_path) as doc:
            text = "\n".join(page.get_text() for page in doc)
        dest.write_text(text, encoding="utf-8")
        converted.append(dest)

    return converted


if __name__ == "__main__":
    convert_books()
