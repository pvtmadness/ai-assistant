# Market Data CSV Intake Design

## Objective

Design the market data intake hierarchy for `BehavioralStateAnalyzer`.

Important correction:

TradingView CSV is only a temporary convenience path for early testing. The preferred production research source should be Sierra Chart because it can provide professional-grade futures data, true volume, bid/ask volume, volume-at-price, Numbers Bars/order-flow data, and better support for Market Profile / Volume Profile work.

This document is design-only. No code is implemented here.

## Data Source Hierarchy

### 1. Prototype Intake

Use TradingView CSV for quick testing only.

Scope:

```text
TradingView CSV
simple OHLCV testing
optional exported VWAP
basic session summary
offline prototype only
```

TradingView is useful for:

- Quick iteration.
- Simple bar-level tests.
- Early CSV loader development.
- Basic VWAP and OHLCV behavioral proxies.

TradingView should not be treated as the long-term research-grade source for profile/order-flow work.

### 2. Preferred Production Research Intake

Use Sierra Chart exports for serious futures research.

Preferred sources:

```text
Sierra Chart export files
Sierra intraday data exports
Sierra volume-at-price data
Sierra Numbers Bars data
Sierra bid/ask volume data
Sierra Market Profile / TPO outputs where exportable
Sierra Volume Profile outputs where exportable
```

Sierra should become the primary source for:

- Futures market research.
- True volume analysis.
- Bid/ask imbalance analysis.
- Absorption and exhaustion research.
- Volume-at-price structure.
- Market Profile / Volume Profile validation.
- Behavioral state backtesting.

### 3. Later Possible Direct Sierra Integration

Later intake paths may include:

```text
reading exported Sierra files
reading Sierra data files if practical
reading saved study outputs
reading volume-at-price exports
reading Numbers Bars exports
```

Explicitly excluded for now:

```text
no live Sierra feed integration
no trading integration
no automated order execution
no real-time alerting
```

The next sensible step is file-based Sierra research intake, not live feed integration.

## Why Sierra Is The Preferred Source

Sierra Chart is preferred because behavioral market structure research needs more than OHLCV bars.

Sierra can support:

- Professional futures data.
- More reliable true volume.
- Bid volume and ask volume.
- Volume at price.
- Numbers Bars / footprint-style data.
- Delta and imbalance analysis.
- Better Market Profile / TPO workflow.
- Better Volume Profile workflow.
- Session-specific profile construction.
- Exportable study outputs.

Behavioral states such as trapped participation, absorption, liquidation, FOMO chase, and fragile auction structure often require order-flow and volume-at-price evidence. TradingView CSV may be enough for early prototype math, but Sierra is better aligned with the actual research goal.

## TradingView Limitations

TradingView CSV is convenient but limited.

Limitations:

- Usually bar-level OHLCV only.
- Indicator columns may depend on what is visible on the chart.
- VWAP export may be inconsistent by indicator/settings.
- Volume Profile details may not export as structured fields.
- Market Profile / TPO structures may not be available in usable CSV form.
- Bid/ask volume is generally unavailable.
- Numbers Bars / footprint detail is unavailable.
- Volume-at-price data is not available in the needed research form.
- Session handling can be ambiguous.
- Futures volume quality may vary by symbol/data source.

Use TradingView as:

```text
quick CSV testing source only
```

Do not use it as:

```text
final behavioral research source
profile validation source
order-flow source
bid/ask imbalance source
```

## Sierra Export Goals

The Sierra export workflow should eventually support:

```text
bar-level intraday exports
volume-at-price exports
Numbers Bars exports
bid/ask volume exports
delta exports
Market Profile / TPO exports where possible
Volume Profile exports where possible
session-specific profile exports
```

Desired workflow:

```text
1. Open a Sierra Chart chartbook for the target futures market.
2. Configure RTH/ETH session settings.
3. Add required studies:
   - VWAP
   - Volume by Price
   - TPO Profile / Market Profile
   - Numbers Bars if needed
   - Cumulative Delta or bar delta if needed
4. Export bar/study/profile data to files.
5. Save exports into a structured local data folder.
6. Run future file intake against exported Sierra files.
7. Build normalized market observation objects.
8. Feed data into BehavioralStateAnalyzer.
```

Suggested local folder:

```text
data/sierra_exports/
```

Example file names:

```text
ES_5m_2026-05-31_sierra_intraday.csv
ES_2026-05-31_sierra_volume_at_price.csv
ES_2026-05-31_sierra_numbers_bars.csv
ES_2026-05-31_sierra_tpo_profile.csv
```

## Data Fields Wanted From Sierra

Minimum bar fields:

```text
Date
Time
Open
High
Low
Last/Close
Volume
Number of Trades
```

Order-flow fields:

```text
Bid Volume
Ask Volume
Delta
Bid/Ask Imbalance
Volume at Price
```

VWAP/profile fields:

```text
VWAP if available
Point of Control
Value Area High
Value Area Low
High Volume Nodes
Low Volume Nodes
Volume Profile distribution
TPO / Market Profile fields if exportable
Single prints
Initial Balance High
Initial Balance Low
Poor High
Poor Low
Excess High
Excess Low
Profile shape
```

Session metadata:

```text
symbol
contract
session_date
session_type
timeframe
timezone
RTH/ETH settings
```

## How Sierra Data Improves Behavioral Analysis

### True Volume

Better volume data improves:

- Consensus detection.
- Participation intensity.
- Value acceptance.
- Volume Profile reliability.

### Bid/Ask Imbalance

Bid/ask data can help identify:

- Aggressive buying.
- Aggressive selling.
- FOMO chase.
- Fear pressure.
- Failed aggression.

### Trapped Participation

Volume-at-price and bid/ask detail can help locate:

- High participation at failed highs/lows.
- Wrong-sided volume after failed breakouts.
- Price zones where participants may become forced buyers or sellers.

### Absorption

Numbers Bars and bid/ask volume may reveal:

- Aggressive buying absorbed by passive sellers.
- Aggressive selling absorbed by passive buyers.
- Failed movement despite strong aggression.

### Liquidation

Sierra order-flow data can help distinguish:

- Normal pullback.
- Stop-driven liquidation.
- Forced selling.
- Short covering.

### FOMO Chase

FOMO pressure can be better evaluated with:

- Aggressive ask lifting.
- Late volume expansion.
- Price extension from VWAP.
- Movement through low-volume areas.

### Fear Pressure

Fear pressure can be better evaluated with:

- Aggressive bid hitting.
- Expanding negative delta.
- VWAP loss.
- Failed reclaim attempts.
- Downside volume-at-price concentration.

### Fragile Auctions

Fragile auction structure can be better evaluated with:

- Thin volume-at-price zones.
- Single prints.
- Poor highs/lows.
- Failed acceptance outside value.
- High volume at vulnerable extremes.

## Prototype TradingView CSV Workflow

TradingView remains useful for the earliest prototype.

Workflow:

```text
1. Open a chart in TradingView.
2. Select instrument and timeframe.
3. Add VWAP if desired.
4. Export chart data as CSV.
5. Save CSV locally.
6. Run future CSV loader.
7. Inspect detected columns.
8. Build simple OHLCV/VWAP session summary.
```

Suggested local folder:

```text
data/market_csv/
```

Example file names:

```text
ES_5m_2026-05-31_tradingview.csv
NQ_5m_2026-05-31_tradingview.csv
CL_15m_2026-05-31_tradingview.csv
```

## Minimum Required TradingView Columns

Required columns:

```text
time
open
high
low
close
volume
```

These columns support:

- Price movement.
- Range.
- Bar direction.
- Session high/low.
- Basic volume intensity.
- Basic VWAP reconstruction if needed.
- Basic behavioral proxy calculation.

## Optional TradingView Columns

Useful optional columns:

```text
VWAP
Volume MA
ATR
Session VWAP
Anchored VWAP
Visible indicator outputs
```

Indicator export caveat:

TradingView column names may vary depending on indicator name, settings, pane, and language. The loader should inspect the file rather than assume exact names.

## How To Inspect Unknown CSV Columns

The future loader should include an inspection mode.

Inspection output should show:

```text
file path
row count
column count
raw column names
first timestamp
last timestamp
first 3 rows
detected OHLCV mapping
detected optional indicators
unknown columns
missing required columns
```

Manual inspection checklist:

```text
1. Open the CSV header row.
2. Confirm time column name.
3. Confirm OHLC columns.
4. Confirm volume column.
5. Look for VWAP-like columns.
6. Look for indicator-generated columns.
7. Identify timezone assumptions.
8. Identify duplicate or empty columns.
```

Unknown columns should not fail the load by default. They should be preserved in a metadata map or ignored with a clear report.

## How To Normalize Column Names

Column normalization should make CSV imports tolerant of naming variations.

Normalization rules:

```text
1. Trim whitespace.
2. Convert to lowercase.
3. Replace spaces with underscores.
4. Remove punctuation where safe.
5. Collapse repeated underscores.
6. Map known aliases to canonical names.
```

Canonical names:

```text
date
time
datetime
open
high
low
close
last
volume
number_of_trades
bid_volume
ask_volume
delta
vwap
```

Possible aliases:

```text
time:
    time
    date
    datetime
    timestamp

close:
    close
    last
    settlement

volume:
    volume
    vol

number_of_trades:
    number of trades
    trades
    num_trades

bid_volume:
    bid volume
    bidvol
    bid_volume

ask_volume:
    ask volume
    askvol
    ask_volume

delta:
    delta
    ask_volume_minus_bid_volume

vwap:
    vwap
    session_vwap
    anchored_vwap
```

## How To Handle Missing VWAP

If VWAP is missing, the prototype can compute a simple session VWAP from OHLCV.

Typical price:

```text
typical_price = (high + low + close) / 3
```

Cumulative VWAP:

```text
cumulative_vwap =
    cumulative_sum(typical_price * volume) / cumulative_sum(volume)
```

Session handling:

```text
1. Identify session boundaries.
2. Reset cumulative VWAP at each session boundary.
3. If session boundaries are unknown, compute file-level VWAP and label confidence lower.
```

VWAP source labels:

```text
vwap_source = exported_tradingview
vwap_source = exported_sierra
vwap_source = computed_session
vwap_source = computed_file_level
vwap_source = unavailable
```

## Volume Profile / Market Profile Field Strategy

TradingView should not be expected to provide full profile structures.

Preferred path:

```text
Sierra Chart profile exports
Sierra volume-at-price exports
Sierra TPO / Market Profile exports where practical
manual sidecar metadata for early experiments
```

Optional sidecar file:

```text
ES_5m_2026-05-31_sierra_intraday.csv
ES_2026-05-31_profile.json
```

Potential sidecar fields:

```text
point_of_control
value_area_high
value_area_low
high_volume_nodes
low_volume_nodes
initial_balance_high
initial_balance_low
single_print_zones
poor_high
poor_low
excess_high
excess_low
profile_shape
```

## Recommended First Prototype

The first prototype should be deliberately small.

### CSV Loader

Responsibilities:

```text
read CSV
validate file exists
parse header
parse rows
parse timestamps
convert numeric OHLCV fields
return normalized bar records
```

### Column Detector

Responsibilities:

```text
normalize column names
map required OHLCV fields
detect optional VWAP field
detect Sierra-specific fields when present
report unknown columns
report missing required fields
report ambiguous mappings
```

### Basic Session Summary

Summary output:

```text
source
symbol if known
row count
timeframe estimate
first timestamp
last timestamp
session high
session low
session open
session close
total volume
average bar volume
number of trades if available
bid volume if available
ask volume if available
delta if available
VWAP source
final VWAP
missing data count
```

### No Live Data

Explicitly excluded from first prototype:

```text
no live TradingView connection
no live Sierra feed integration
no broker API
no websocket feed
no order execution
no live alerts
```

## Future Analyzer Integration

Conceptual normalized output:

```python
MarketDataFrame:
    source: "tradingview_csv" | "sierra_export"
    symbol: str | None
    timeframe: str | None
    rows: list[Bar]
    columns: dict[str, str]
    vwap_source: str
    warnings: list[str]

Bar:
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    number_of_trades: int | None
    bid_volume: float | None
    ask_volume: float | None
    delta: float | None
    vwap: float | None
```

Analyzer handoff:

```text
MarketDataFrame
    -> SessionSummary
    -> optional ProfileMetadata
    -> BehavioralStateAnalyzer
    -> BehavioralState
```

## Design Constraints

- No code yet.
- No live data.
- No broker integration.
- No automated trading.
- TradingView is quick-test only.
- Sierra is preferred for production research.
- Prefer transparent CSV/file inspection over hidden assumptions.
- Preserve raw column names for debugging.
- Keep derived fields labeled by source and confidence.

## Open Questions

1. Which Sierra export format should become the first supported production research path?
2. Can Sierra export volume-at-price in a stable parseable format?
3. Can Sierra export Numbers Bars / bid-ask volume in a stable parseable format?
4. What is the best sidecar format for profile metadata: JSON, CSV, or YAML?
5. Should RTH/ETH session splitting be controlled by Sierra export settings or by the loader?
6. Should symbol and timeframe be inferred from filename?
7. How should missing or zero volume bars be handled?
8. How should continuous futures symbols be normalized?
9. How should TradingView and Sierra exports be compared during prototype validation?
