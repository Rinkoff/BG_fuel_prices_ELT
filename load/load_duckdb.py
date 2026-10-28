"""
Convert raw JSON to DuckDB table `raw.fuel_prices`.

Reads the latest raw snapshot, reshapes the "wide" parallel arrays into tidy
rows (one row per week x fuel), and loads them into DuckDB. Heavier cleaning
and modelling happens later in dbt.
"""
import json
from pathlib import Path

import duckdb

#Paths
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "warehouse.duckdb"

# Fuels
FUELS = ["e95", "diesel"]


def latest_raw_file() -> Path:
    """Find the latest snapshot."""
    files = sorted(RAW_DIR.glob("fetch_date=*/bg_history.json"))
    if not files:
        raise FileNotFoundError(
            "No raw file found. Run 'python ingest/fetch_prices.py' first."
        )
    return files[-1]


def reshape(payload: dict) -> list[tuple]:
    """Turn the wide arrays into tidy rows: (week_date, fuel_code, price)."""
    weeks = payload["labels"]
    rows: list[tuple] = []
    for fuel in FUELS:
        prices = payload[fuel]
        for week, price in zip(weeks, prices):
            rows.append((week, fuel, price))
    return rows


def load(rows: list[tuple]) -> int:
    """Craete the raw table in DuckDB and insert the rows."""
    con = duckdb.connect(str(DB_PATH))
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

        con.execute(
            """
            CREATE OR REPLACE TABLE raw.fuel_prices (
                price_date DATE,
                fuel_code  VARCHAR,
                price_eur  DOUBLE
            );
            """
        )
        con.executemany(
            "INSERT INTO raw.fuel_prices VALUES (?, ?, ?);", rows
        )
        count = con.execute("SELECT count(*) FROM raw.fuel_prices;").fetchone()[0]
        return count
    finally:
        con.close()


def main() -> None:
    src = latest_raw_file()
    print(f"Reading raw file: {src}")

    payload = json.loads(src.read_text(encoding="utf-8"))
    rows = reshape(payload)
    print(f"Reshaped into {len(rows)} tidy rows (weeks x fuels).")

    count = load(rows)
    print(f"Loaded {count} rows into raw.fuel_prices ({DB_PATH.name}).")


if __name__ == "__main__":
    main()
