import argparse
import csv
import sqlite3
from pathlib import Path

from app.market.catalog import MarketImportCatalog


CATALOG_PATH = Path("data/market/catalog.sqlite")
UNAVAILABLE = "unavailable"


def read_time_range(processed_path: Path) -> tuple[str, str]:
    if not processed_path.exists() or not processed_path.is_file():
        return UNAVAILABLE, UNAVAILABLE

    with processed_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "timestamp" not in reader.fieldnames:
            return UNAVAILABLE, UNAVAILABLE

        start_time = None
        end_time = None
        for row in reader:
            timestamp = (row.get("timestamp") or "").strip()
            if not timestamp:
                continue
            if start_time is None:
                start_time = timestamp
            end_time = timestamp

    return start_time or UNAVAILABLE, end_time or UNAVAILABLE


def list_datasets() -> int:
    if not CATALOG_PATH.exists():
        print("No market datasets found.")
        return 0

    try:
        records = MarketImportCatalog(CATALOG_PATH).list_imports()
    except sqlite3.Error:
        print("No market datasets found.")
        return 0

    if not records:
        print("No market datasets found.")
        return 0

    print("source | symbol | timeframe | rows | start_time | end_time | processed_path")
    for record in records:
        start_time, end_time = read_time_range(record.processed_path)
        print(
            f"{record.source} | {record.symbol} | {record.timeframe} | "
            f"{record.row_count} | {start_time} | {end_time} | {record.processed_path}"
        )

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect locally imported market datasets.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List imported market datasets.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list":
        return list_datasets()

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
