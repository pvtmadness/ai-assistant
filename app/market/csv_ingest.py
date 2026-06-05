import argparse
import csv
import hashlib
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from app.market.catalog import MarketImportCatalog
from app.market.chroma_index import index_import_summary
from app.market.schemas import MarketBar, MarketImportMetadata


RAW_DIR = Path("data/market/raw")
PROCESSED_DIR = Path("data/market/processed")


class CsvIngestError(ValueError):
    pass


class MarketCsvAdapter:
    source = "generic"

    column_aliases = {
        "time": "timestamp",
        "timestamp": "timestamp",
        "date": "date",
        "datetime": "timestamp",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "last": "close",
        "volume": "volume",
        "vol": "volume",
    }

    required_columns = {"timestamp", "open", "high", "low", "close", "volume"}

    def normalize_column(self, name: str) -> str:
        normalized = (
            name.strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )
        return self.column_aliases.get(normalized, normalized)

    def normalize_row(self, row: dict[str, str]) -> dict[str, str]:
        normalized = {
            self.normalize_column(key): value.strip()
            for key, value in row.items()
            if key is not None and value is not None
        }
        if "timestamp" not in normalized and {"date", "time"} <= set(normalized):
            normalized["timestamp"] = f"{normalized['date']} {normalized['time']}"
        return normalized

    def normalized_columns(self, columns: Iterable[str]) -> set[str]:
        normalized = {self.normalize_column(column) for column in columns}
        if {"date", "time"} <= normalized:
            normalized.add("timestamp")
        return normalized


class TradingViewCsvAdapter(MarketCsvAdapter):
    source = "tradingview"


class SierraCsvAdapter(MarketCsvAdapter):
    source = "sierra"

    column_aliases = {
        **MarketCsvAdapter.column_aliases,
        "date": "date",
        "time": "time",
        "date_time": "timestamp",
        "date__time": "timestamp",
        "last_close": "close",
        "last_close_price": "close",
        "total_volume": "volume",
    }


ADAPTERS = {
    "tradingview": TradingViewCsvAdapter,
    "sierra": SierraCsvAdapter,
}


def get_adapter(source: str) -> MarketCsvAdapter:
    normalized = source.strip().lower()
    adapter_cls = ADAPTERS.get(normalized)
    if adapter_cls is None:
        raise CsvIngestError(
            f"Unsupported source '{source}'. Expected one of: {', '.join(sorted(ADAPTERS))}"
        )
    return adapter_cls()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_timestamp(value: str) -> datetime:
    raw = value.strip()
    if not raw:
        raise CsvIngestError("Missing timestamp value")

    candidates = [
        raw,
        raw.replace("Z", "+00:00"),
    ]

    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            pass

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
        except ValueError:
            pass

    raise CsvIngestError(f"Unsupported timestamp format: {value}")


def parse_float(row: dict[str, str], column: str, row_number: int) -> float:
    value = row.get(column, "")
    try:
        return float(value.replace(",", ""))
    except ValueError as exc:
        raise CsvIngestError(
            f"Invalid {column} value on row {row_number}: {value}"
        ) from exc


def validate_columns(columns: Iterable[str], adapter: MarketCsvAdapter) -> None:
    normalized = adapter.normalized_columns(columns)
    missing = sorted(adapter.required_columns - normalized)
    if missing:
        raise CsvIngestError(f"Missing required OHLCV columns: {', '.join(missing)}")


def validate_bar(bar: MarketBar, row_number: int) -> None:
    if bar.high < max(bar.open, bar.close, bar.low):
        raise CsvIngestError(f"Invalid OHLC relationship on row {row_number}: high too low")
    if bar.low > min(bar.open, bar.close, bar.high):
        raise CsvIngestError(f"Invalid OHLC relationship on row {row_number}: low too high")
    if bar.volume < 0:
        raise CsvIngestError(f"Invalid volume on row {row_number}: volume cannot be negative")


def load_csv(path: Path, source: str, symbol: str, timeframe: str) -> list[MarketBar]:
    adapter = get_adapter(source)

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise CsvIngestError("CSV file has no header row")

        validate_columns(reader.fieldnames, adapter)

        bars = []
        for row_number, raw_row in enumerate(reader, start=2):
            row = adapter.normalize_row(raw_row)
            bar = MarketBar(
                timestamp=parse_timestamp(row["timestamp"]),
                open=parse_float(row, "open", row_number),
                high=parse_float(row, "high", row_number),
                low=parse_float(row, "low", row_number),
                close=parse_float(row, "close", row_number),
                volume=parse_float(row, "volume", row_number),
                symbol=symbol.upper(),
                timeframe=timeframe,
                source=adapter.source,
            )
            validate_bar(bar, row_number)
            bars.append(bar)

    if not bars:
        raise CsvIngestError("CSV file contains no data rows")

    return bars


def copy_raw_file(source_path: Path, import_id: str, file_hash: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    destination = RAW_DIR / f"{import_id}_{file_hash[:12]}_{source_path.name}"
    shutil.copy2(source_path, destination)
    return destination


def save_processed_bars(bars: list[MarketBar], import_id: str, symbol: str, timeframe: str) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    destination = PROCESSED_DIR / f"{import_id}_{symbol.upper()}_{timeframe}.csv"

    with destination.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "symbol",
                "timeframe",
                "source",
            ],
        )
        writer.writeheader()
        for bar in bars:
            writer.writerow(
                {
                    "timestamp": bar.timestamp.isoformat(),
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume,
                    "symbol": bar.symbol,
                    "timeframe": bar.timeframe,
                    "source": bar.source,
                }
            )

    return destination


def ingest_csv(
    csv_path: str | Path,
    source: str,
    symbol: str,
    timeframe: str,
    index_chroma: bool = True,
    catalog: MarketImportCatalog | None = None,
) -> MarketImportMetadata:
    source_path = Path(csv_path)
    if not source_path.exists():
        raise CsvIngestError(f"CSV file not found: {source_path}")
    if not source_path.is_file():
        raise CsvIngestError(f"CSV path is not a file: {source_path}")

    catalog = catalog or MarketImportCatalog()
    file_hash = file_sha256(source_path)
    duplicate = catalog.find_by_hash(file_hash)
    if duplicate:
        raise CsvIngestError(
            f"Duplicate import skipped: file already imported as {duplicate.import_id}"
        )

    import_id = str(uuid.uuid4())
    raw_path = copy_raw_file(source_path, import_id, file_hash)
    bars = load_csv(raw_path, source=source, symbol=symbol, timeframe=timeframe)
    processed_path = save_processed_bars(bars, import_id, symbol=symbol, timeframe=timeframe)

    metadata = MarketImportMetadata(
        import_id=import_id,
        source=source.strip().lower(),
        symbol=symbol.upper(),
        timeframe=timeframe,
        original_path=source_path,
        raw_path=raw_path,
        processed_path=processed_path,
        file_hash=file_hash,
        row_count=len(bars),
        imported_at=datetime.now(UTC),
        chroma_status="not_requested",
    )

    if index_chroma:
        metadata = MarketImportMetadata(
            **{
                **metadata.__dict__,
                "chroma_status": index_import_summary(metadata, bars),
            }
        )

    catalog.add_import(metadata)
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import OHLCV market data from CSV.")
    parser.add_argument("csv_path", help="Path to a TradingView or Sierra OHLCV CSV file.")
    parser.add_argument(
        "--source",
        required=True,
        choices=sorted(ADAPTERS),
        help="CSV source adapter.",
    )
    parser.add_argument("--symbol", required=True, help="Market symbol, e.g. ES, MES, MCL.")
    parser.add_argument("--timeframe", required=True, help="Bar timeframe, e.g. 1m, 5m, 1d.")
    parser.add_argument(
        "--no-chroma",
        action="store_true",
        help="Skip optional Chroma summary indexing.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        metadata = ingest_csv(
            args.csv_path,
            source=args.source,
            symbol=args.symbol,
            timeframe=args.timeframe,
            index_chroma=not args.no_chroma,
        )
    except CsvIngestError as exc:
        print(f"[Market-Import] failed | {exc}")
        return 1

    print(f"[Market-Import] import_id={metadata.import_id}")
    print(f"[Market-Import] source={metadata.source} symbol={metadata.symbol} timeframe={metadata.timeframe}")
    print(f"[Market-Import] rows={metadata.row_count}")
    print(f"[Market-Import] raw_path={metadata.raw_path}")
    print(f"[Market-Import] processed_path={metadata.processed_path}")
    print(f"[Market-Import] chroma_status={metadata.chroma_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
