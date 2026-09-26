import csv
import re
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "books.csv"
BOOKS_DIR = BASE_DIR / "data" / "books_pdf"


def slugify(title: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
    return re.sub(r"[\s_-]+", "_", slug)


def download_books(
        csv_path: Path = CSV_PATH,
        books_dir: Path = BOOKS_DIR,
        ) -> list[Path]:
    books_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title", "").strip()
            pdf_url = row.get("pdf_url", "").strip()
            if not title or not pdf_url:
                continue

            dest = books_dir / f"{slugify(title)}.pdf"
            if dest.exists():
                print(f"Skipping (already exists): {dest.name}")
                downloaded.append(dest)
                continue

            print(f"Downloading {title} -> {dest.name}")
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()
            dest.write_bytes(response.content)
            downloaded.append(dest)

    return downloaded


if __name__ == "__main__":
    download_books()
