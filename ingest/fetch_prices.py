"""
Fetch Bulgaria's fuel-price history from fuel-prices.eu.

This makes HTTP request and saves the raw JSON response.
"""

import json
from datetime import date
from pathlib import Path

import requests

# Fetch from:
API_URL = "https://www.fuel-prices.eu/lang/api/country-history.php"
PARAMS = {"cc": "BG"}  # cc = country code; BG = Bulgaria

# Saved in <root/data/raw>
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch() -> dict:
    """Ask the API for Bulgaria's price history and return it as a dict."""
    response = requests.get(API_URL, params=PARAMS, timeout=30)
    response.raise_for_status()  # stop with an error if the request failed
    return response.json()


def save(payload: dict) -> Path:
    """Write the raw JSON to data/raw/fetch_date=YYYY-MM-DD/bg_history.json."""
    today = date.today().isoformat()
    out_dir = RAW_DIR / f"fetch_date={today}"
    out_dir.mkdir(parents=True, exist_ok=True)  # create folders if missing

    out_path = out_dir / "bg_history.json"
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_path


def main() -> None:
    print("Fetching BG fuel-price history from fuel-prices.eu ...")
    payload = fetch()
    path = save(payload)

    weeks = len(payload.get("labels", []))  # just a sanity-check count
    print(f"Done. Saved {weeks} weeks of data -> {path}")


if __name__ == "__main__":
    main()
