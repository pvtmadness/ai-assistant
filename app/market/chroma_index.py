from app.market.schemas import MarketBar, MarketImportMetadata


def build_import_summary(metadata: MarketImportMetadata, bars: list[MarketBar]) -> str:
    if bars:
        first_timestamp = min(bar.timestamp for bar in bars).isoformat()
        last_timestamp = max(bar.timestamp for bar in bars).isoformat()
        high = max(bar.high for bar in bars)
        low = min(bar.low for bar in bars)
        total_volume = sum(bar.volume for bar in bars)
    else:
        first_timestamp = "n/a"
        last_timestamp = "n/a"
        high = 0
        low = 0
        total_volume = 0

    return "\n".join(
        [
            "Market data import summary",
            f"Import ID: {metadata.import_id}",
            f"Source: {metadata.source}",
            f"Symbol: {metadata.symbol}",
            f"Timeframe: {metadata.timeframe}",
            f"Rows: {metadata.row_count}",
            f"Start: {first_timestamp}",
            f"End: {last_timestamp}",
            f"High: {high}",
            f"Low: {low}",
            f"Total volume: {total_volume}",
            f"Processed file: {metadata.processed_path}",
        ]
    )


def index_import_summary(metadata: MarketImportMetadata, bars: list[MarketBar]) -> str:
    summary = build_import_summary(metadata, bars)

    try:
        from app.memory.store import memory_store

        memory_store.add(
            summary,
            memory_id=f"market-import-{metadata.import_id}",
            domain="trading",
            memory_type="reference",
        )
    except Exception as exc:
        return f"unavailable: {exc}"

    return "stored"
