import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.market.schemas import MarketImportMetadata


@dataclass(frozen=True)
class CatalogRecord:
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
    chroma_status: str


class MarketImportCatalog:
    def __init__(self, db_path: str | Path = "data/market/catalog.sqlite") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._setup()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _setup(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS market_imports (
                    import_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    original_path TEXT NOT NULL,
                    raw_path TEXT NOT NULL,
                    processed_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,
                    row_count INTEGER NOT NULL,
                    imported_at TEXT NOT NULL,
                    chroma_status TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_market_imports_symbol_timeframe
                ON market_imports (symbol, timeframe)
                """
            )

    def find_by_hash(self, file_hash: str) -> CatalogRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT import_id, source, symbol, timeframe, original_path, raw_path,
                       processed_path, file_hash, row_count, imported_at, chroma_status
                FROM market_imports
                WHERE file_hash = ?
                """,
                (file_hash,),
            ).fetchone()

        if row is None:
            return None

        return CatalogRecord(
            import_id=row[0],
            source=row[1],
            symbol=row[2],
            timeframe=row[3],
            original_path=Path(row[4]),
            raw_path=Path(row[5]),
            processed_path=Path(row[6]),
            file_hash=row[7],
            row_count=row[8],
            imported_at=datetime.fromisoformat(row[9]),
            chroma_status=row[10],
        )

    def add_import(self, metadata: MarketImportMetadata) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO market_imports (
                    import_id, source, symbol, timeframe, original_path, raw_path,
                    processed_path, file_hash, row_count, imported_at, chroma_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metadata.import_id,
                    metadata.source,
                    metadata.symbol,
                    metadata.timeframe,
                    str(metadata.original_path),
                    str(metadata.raw_path),
                    str(metadata.processed_path),
                    metadata.file_hash,
                    metadata.row_count,
                    metadata.imported_at.astimezone(UTC).isoformat(),
                    metadata.chroma_status,
                ),
            )

    def update_chroma_status(self, import_id: str, chroma_status: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE market_imports
                SET chroma_status = ?
                WHERE import_id = ?
                """,
                (chroma_status, import_id),
            )
