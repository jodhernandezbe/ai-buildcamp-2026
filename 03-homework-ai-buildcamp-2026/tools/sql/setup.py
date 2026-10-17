import urllib.request
from pathlib import Path

import duckdb

DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PARQUET_FILE = DATA_DIR / "yellow_tripdata_2024-01.parquet"
DB_FILE = DATA_DIR / "taxi.db"


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open the DuckDB database stored in the data folder."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_FILE))


def setup_database():
    """Download the parquet file and load it into DuckDB."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PARQUET_FILE.exists():
        print(f"Downloading {DATA_URL}...")
        urllib.request.urlretrieve(DATA_URL, PARQUET_FILE)

    con = get_connection()
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS trips AS
        SELECT * FROM '{PARQUET_FILE}'
    """)
    row = con.execute("SELECT COUNT(*) FROM trips").fetchone()
    count = row[0] if row else 0
    print(f"Loaded {count} rows")
    con.close()
    return count


if __name__ == "__main__":
    count = setup_database()
    print(f"Number of rows in the January 2024 dataset: {count}")
