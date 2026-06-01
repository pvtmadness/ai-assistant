# Sierra Data Requirements

## 1. Objective

Map `BehavioralStateAnalyzer` variables to the specific Sierra Chart data, studies, and export paths needed for production-quality futures market research.

Sierra Chart is the preferred production research source because it can provide professional futures data, true volume, bid/ask volume, volume-at-price, Numbers Bars/order-flow data, VWAP study output, and better support for Market Profile / Volume Profile work.

TradingView CSV remains useful only as a temporary convenience path for simple OHLCV/VWAP prototype testing.

## Current Sierra Setup

Current known setup:

```text
Platform: Sierra Chart
Data: Denali
Intended role: primary research platform
TradingView role: quick prototype CSV testing only
```

The current Sierra Chart service level appears to support the core research workflows needed for the first phase:

```text
TPO / Market Profile work
Volume Profile work
Numbers Bars / footprint-style work
intraday futures data
bar-level bid volume / ask volume where exportable
study outputs such as VWAP where exportable
```

This setup should be treated as the baseline production research environment for `BehavioralStateAnalyzer`.

TradingView remains useful only for:

```text
quick CSV loader testing
simple OHLCV checks
rough VWAP prototype testing
```

Higher Sierra data capabilities with extended bid/offer depth may be added later if the research needs deeper order-book behavior.

## Data Depth Upgrade Consideration

The current Denali setup should be sufficient for the first export experiments.

Do not require a Sierra data-level upgrade for the first prototype.

Extended market depth or deeper bid/offer depth may become useful later for:

```text
absorption analysis
liquidity stacking
liquidity pulling
resting order-book behavior
depth imbalance
spoofing-like behavior research
pre-breakout liquidity changes
failed breakout liquidity response
```

Potential future use cases:

- Confirming whether aggressive buying is being absorbed by stacked offers.
- Detecting liquidity pulling before fast movement.
- Studying whether fragile auctions coincide with thin depth.
- Distinguishing true participation from movement through shallow liquidity.
- Adding deeper context to trapped participation and liquidation analysis.

For the first prototype, prioritize:

```text
intraday export
bid volume
ask volume
delta
VWAP
Volume Profile / volume-at-price
TPO / Market Profile fields or sidecar metadata
```

Deeper order-book data should be considered a later enhancement, not a blocker.

## 2. Sierra Data Sources To Investigate

Investigate these Sierra Chart data sources and export mechanisms:

```text
Intraday data text export
.scid intraday data files
Volume by Price
TPO / Market Profile
Numbers Bars
Bid Volume
Ask Volume
Delta
VWAP study output
study spreadsheet/export options if available
```

Research questions:

- Which exports are easiest to automate?
- Which exports preserve timestamps cleanly?
- Which exports include bid/ask volume by bar?
- Which exports include volume-at-price by price level?
- Can TPO / Market Profile structures be exported directly?
- Can study subgraphs such as VWAP be included in spreadsheet/export output?
- Is reading `.scid` files practical, or should initial work use text exports only?

## 3. Required Fields By Layer

### Bar-Level Data

Required:

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

Used for:

- Session range.
- Price velocity.
- Basic volume intensity.
- OHLCV-only prototype scoring.
- VWAP reconstruction if exported VWAP is unavailable.

### Bid/Ask Volume

Required:

```text
Bid Volume
Ask Volume
Delta
```

Derived:

```text
delta = ask_volume - bid_volume
total_aggressive_volume = ask_volume + bid_volume
ask_ratio = ask_volume / total_aggressive_volume
bid_ratio = bid_volume / total_aggressive_volume
```

Used for:

- FOMO chase.
- Fear pressure.
- Absorption.
- Liquidation.
- Trapped participation.
- Failed aggression.

### Volume-At-Price

Required if available:

```text
price_level
volume_at_price
bid_volume_at_price
ask_volume_at_price
delta_at_price
```

Used for:

- High-volume nodes.
- Low-volume nodes.
- Trapped participation zones.
- Absorption zones.
- Volume Profile construction.
- Fragile auction structure.

### TPO / Market Profile

Required if exportable:

```text
TPO count by price
time at price
initial balance high
initial balance low
single prints
poor high
poor low
excess high
excess low
profile shape
day type
```

Used for:

- Consensus.
- Unfinished auctions.
- Failed auctions.
- Profile maturity.
- Value acceptance.
- Rotation versus trend behavior.

### VWAP

Preferred:

```text
VWAP study output
VWAP bands if useful
```

Fallback:

```text
computed session VWAP from OHLCV
```

Used for:

- Distance from average participation price.
- VWAP reclaim/loss.
- VWAP slope.
- Time above/below VWAP.
- Pullback absorption.

### Session Metadata

Required:

```text
symbol
contract
session_date
session_type
timezone
RTH start
RTH end
ETH start
ETH end
timeframe
tick size
point value
data source
export method
```

Used for:

- RTH/ETH separation.
- Prior day comparison.
- Contract normalization.
- Profile maturity.
- Research reproducibility.

## 4. Behavioral State To Sierra Evidence Map

### Consensus

Sierra evidence:

```text
bar-level OHLCV
VWAP study output
Volume by Price
TPO / Market Profile
time at price
volume at price
POC
Value Area High
Value Area Low
```

Useful measurements:

- Time inside value area.
- Volume inside value area.
- VWAP reversion frequency.
- POC stability.
- TPO concentration near value.

Best Sierra sources:

```text
Intraday data export
VWAP study output
Volume by Price export
TPO / Market Profile export
```

### FOMO Pressure

Sierra evidence:

```text
price extension from VWAP
relative volume
ask volume expansion for upside chase
bid volume expansion for downside chase
single prints
low-volume node traversal
initial balance breakout
```

Useful measurements:

- Distance from VWAP.
- Relative volume.
- Ask/bid volume imbalance.
- Time outside value.
- Single-print count.
- Movement through low-volume areas.

Best Sierra sources:

```text
Intraday data export
Bid Volume / Ask Volume
Numbers Bars
VWAP study output
Volume by Price
TPO / Market Profile
```

### Fear Pressure

Sierra evidence:

```text
downside price velocity
bid volume expansion
negative delta
VWAP loss
failed VWAP reclaim
break below value
downside single prints
b-shaped profile
```

Useful measurements:

- Bid volume surge.
- Negative delta.
- Time below VWAP.
- Failed reclaim attempts.
- Volume concentration below value.

Best Sierra sources:

```text
Intraday data export
Bid Volume / Ask Volume
Delta
Numbers Bars
VWAP study output
TPO / Market Profile
```

### Conviction

Sierra evidence:

```text
VWAP slope
time above/below VWAP
POC migration
value area migration
directional volume at price
pullback absorption
single prints that remain unrepaired
```

Useful measurements:

- VWAP alignment.
- POC shift.
- Value area shift.
- Pullbacks holding above/below VWAP.
- Volume building in direction of movement.

Best Sierra sources:

```text
Intraday data export
VWAP study output
Volume by Price
TPO / Market Profile
Numbers Bars
```

### Crowd Fragility

Sierra evidence:

```text
high volume at vulnerable extremes
thin volume-at-price zones
failed acceptance outside value
poor high / poor low
single prints behind price
VWAP extension
bid/ask imbalance failure
```

Useful measurements:

- Volume concentration at failed extreme.
- Low-volume area size near current price.
- Distance from VWAP.
- Failed acceptance events.
- Aggressive buying/selling failure.

Best Sierra sources:

```text
Volume by Price
Numbers Bars
Bid Volume / Ask Volume
Delta
VWAP study output
TPO / Market Profile
```

### Regret Potential

Sierra evidence:

```text
break from mature balance
thin re-entry zones
single prints
failed return to prior value
late volume expansion
old POC abandonment
```

Useful measurements:

- Prior balance maturity.
- Distance from old value.
- Time offered for pullback.
- Volume appearing after movement.
- Failure to retest old value.

Best Sierra sources:

```text
Intraday data export
Volume by Price
TPO / Market Profile
VWAP study output
Bid Volume / Ask Volume
```

### Belief Acceleration

Sierra evidence:

```text
price velocity increase
volume acceleration
delta acceleration
VWAP slope change
rapid POC shift
single prints
low-volume node traversal
```

Useful measurements:

- Price acceleration.
- Relative volume acceleration.
- Delta change rate.
- VWAP slope change.
- Value migration velocity.

Best Sierra sources:

```text
Intraday data export
Bid Volume / Ask Volume
Delta
VWAP study output
Volume by Price
TPO / Market Profile
```

### Value Migration

Sierra evidence:

```text
POC migration
Value Area High migration
Value Area Low migration
new high-volume node formation
old value rejection
time building in new distribution
double distribution
```

Useful measurements:

- POC shift.
- Value midpoint shift.
- Time in new value area.
- Volume in new value area.
- Failed returns to old value.

Best Sierra sources:

```text
Volume by Price
TPO / Market Profile
Intraday data export
VWAP study output
```

### Trapped Participation

Sierra evidence:

```text
high volume at failed breakout/breakdown
failed acceptance outside value
return through high-participation zone
VWAP reclaim/loss against participants
aggressive bid/ask failure
delta reversal
```

Useful measurements:

- Volume at failed level.
- Bid/ask imbalance at failed level.
- Return speed through participation zone.
- VWAP cross after failed move.
- Delta divergence or reversal.

Best Sierra sources:

```text
Volume by Price
Numbers Bars
Bid Volume / Ask Volume
Delta
VWAP study output
TPO / Market Profile
```

## 5. States Approximable With OHLCV Only

These can be approximated with OHLCV, but confidence should be reduced:

```text
Consensus
FOMO Pressure
Fear Pressure
Conviction
Belief Acceleration
Value Migration
```

OHLCV approximation examples:

- Consensus from range compression, volume concentration by bar, and VWAP if computed.
- FOMO from price extension and relative volume.
- Fear from downside velocity and volume expansion.
- Conviction from directional persistence and VWAP alignment.
- Belief Acceleration from price and volume acceleration.
- Value Migration from session-level price acceptance, if profile data is unavailable.

Limitations:

- OHLCV cannot reliably identify bid/ask aggression.
- OHLCV cannot precisely locate volume-at-price.
- OHLCV cannot distinguish absorption from lack of participation.
- OHLCV cannot reliably identify trapped participation.

## 6. States Requiring Sierra Order-Flow / Profile Data

These require Sierra-style profile/order-flow data for serious research:

```text
Crowd Fragility
Regret Potential
Trapped Participation
Absorption-related Conviction
Failed Auction Repair
Liquidation versus normal pullback
```

Required evidence:

```text
bid volume
ask volume
delta
volume at price
Numbers Bars
TPO / Market Profile
Volume by Price
```

Why:

- Fragility requires knowing where participation is concentrated and where structure is thin.
- Regret Potential requires knowing where participants were left behind or trapped.
- Trapped Participation requires knowing whether meaningful volume transacted at failed levels.
- Absorption requires comparing aggression against price progress.

## 7. Recommended First Sierra Export Experiment

Start with one liquid futures session.

Instrument:

```text
ES or MES
```

Session:

```text
one RTH session
```

Initial export:

```text
5-minute intraday export
Bid Volume included if possible
Ask Volume included if possible
Delta included if possible
VWAP visible/exported if possible
```

Profile data:

```text
Volume Profile as separate export if possible
TPO / Market Profile as separate export if possible
manual profile sidecar if export is not practical
```

Manual sidecar fallback:

```text
point_of_control
value_area_high
value_area_low
initial_balance_high
initial_balance_low
poor_high
poor_low
single_print_zones
profile_shape
```

Experiment goals:

- Confirm Sierra export format.
- Confirm timestamp parsing.
- Confirm bid/ask volume availability.
- Confirm VWAP export feasibility.
- Identify practical path for profile fields.
- Compare Sierra output against TradingView CSV for same session.

## 8. Proposed Folder Structure

```text
data/
  sierra_exports/
    intraday/
    volume_at_price/
    numbers_bars/
    tpo_profile/
    vwap/

  profile_sidecars/

  market_csv/
```

Suggested files:

```text
data/sierra_exports/intraday/ES_2026-05-31_RTH_5m.csv
data/sierra_exports/volume_at_price/ES_2026-05-31_RTH_vap.csv
data/sierra_exports/numbers_bars/ES_2026-05-31_RTH_numbers_bars.csv
data/sierra_exports/tpo_profile/ES_2026-05-31_RTH_tpo.csv
data/profile_sidecars/ES_2026-05-31_RTH_profile.json
data/market_csv/ES_2026-05-31_tradingview_5m.csv
```

## 9. TradingView Role

TradingView remains a temporary prototype path only.

Use TradingView for:

```text
quick CSV loader testing
basic OHLCV validation
computed VWAP testing
rough prototype demos
```

Do not rely on TradingView for:

```text
production futures research
bid/ask volume
Numbers Bars
volume-at-price
true profile reconstruction
trapped participation research
absorption research
liquidation research
```

## 10. Open Questions

1. Which Sierra text export format provides the cleanest bid/ask volume columns?
2. Can Sierra export Numbers Bars in a stable, parseable file?
3. Can Sierra export volume-at-price by session in a practical format?
4. Can TPO / Market Profile fields be exported directly, or should they be sidecar metadata first?
5. Should `.scid` parsing be avoided until text exports are proven insufficient?
6. How should RTH and ETH profiles be separated in exported files?
7. Should the first experiment use ES for liquidity or MES for accessibility?
8. How should contract rollover and continuous contracts be represented?
9. How should Sierra exports be versioned so historical research is reproducible?
