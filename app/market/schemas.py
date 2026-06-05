from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class MarketBar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str
    timeframe: str
    source: str


@dataclass(frozen=True)
class MarketImportMetadata:
    import_id: str
    source: str
    symbol: str
    timeframe: str
    original_path: Path
    raw_path: Path
    processed_path: Path
    file_hash: str
    row_count: int
    imported_at: datetime
    chroma_status: str = "not_requested"


# TODO: Add MarketFootprintBar for Sierra Numbers Bars / footprint exports.
# TODO: Add MarketVolumeAtPriceRow for Sierra volume-at-price/profile exports.
