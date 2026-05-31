# Behavioral State Analyzer Prototype Design

## Objective

Design the first implementation version of `BehavioralStateAnalyzer`.

Prototype scope is intentionally narrow. It only scores:

- Consensus
- FOMO Pressure
- Crowd Fragility

The prototype uses only:

- Price
- Volume
- VWAP
- Volume Profile
- Market Profile

This document is design-only. It does not add code or define final trading signals.

## Prototype Principles

The first version should be simple, explainable, and testable.

Each state should produce:

```text
score:      0.0 to 1.0
confidence: 0.0 to 1.0
evidence:   human-readable notes
```

Suggested interpretation:

```text
0.00 - 0.24 = absent / weak
0.25 - 0.49 = mild
0.50 - 0.74 = moderate
0.75 - 1.00 = strong
```

All raw values should be normalized before scoring.

## BehavioralState Object

Design-only object:

```python
BehavioralState:
    symbol: str
    session_id: str
    timestamp: datetime

    consensus_score: float
    consensus_confidence: float

    fomo_pressure_score: float
    fomo_pressure_confidence: float

    crowd_fragility_score: float
    crowd_fragility_confidence: float

    dominant_state: str
    evidence: list[str]
    warnings: list[str]
```

Optional nested shape:

```python
StateScore:
    name: str
    score: float
    confidence: float
    inputs_used: dict[str, float]
    evidence: list[str]
```

## Required Charting Platform Data

The prototype needs a charting platform or data export to provide:

### Price

```text
current_price
session_open
session_high
session_low
prior_close
bar_high
bar_low
bar_close
bar_timestamp
```

### Volume

```text
bar_volume
cumulative_session_volume
average_bar_volume
relative_volume
volume_by_price
```

### VWAP

```text
current_vwap
vwap_history
vwap_slope
time_above_vwap
time_below_vwap
vwap_test_count
vwap_reversion_count
```

### Volume Profile

```text
point_of_control
value_area_high
value_area_low
value_area_volume
total_profile_volume
high_volume_nodes
low_volume_nodes
volume_at_current_price
volume_at_breakout_area
```

### Market Profile

```text
time_at_price
tpo_count_by_price
initial_balance_high
initial_balance_low
single_print_zones
profile_day_type
time_inside_value_area
time_outside_value_area
```

## Shared Normalized Inputs

The prototype should compute normalized inputs before scoring.

```text
range = session_high - session_low

distance_from_vwap =
    abs(current_price - current_vwap)

normalized_vwap_distance =
    distance_from_vwap / max(range, small_number)

price_location_in_value =
    1.0 if value_area_low <= current_price <= value_area_high else 0.0

time_inside_value_ratio =
    time_inside_value_area / max(total_session_time, small_number)

volume_inside_value_ratio =
    value_area_volume / max(total_profile_volume, small_number)

relative_volume =
    bar_volume / max(average_bar_volume, small_number)

profile_balance_ratio =
    volume_inside_value_ratio * time_inside_value_ratio
```

Clamp normalized scores:

```text
clamped_score = min(max(raw_score, 0.0), 1.0)
```

## 1. Consensus

### Inputs

Required:

```text
time_inside_value_ratio
volume_inside_value_ratio
normalized_vwap_distance
vwap_reversion_ratio
market_profile_balance_score
```

Definitions:

```text
vwap_reversion_ratio =
    vwap_reversion_count / max(vwap_test_count, 1)

vwap_acceptance_score =
    1.0 - min(normalized_vwap_distance / 0.25, 1.0)

market_profile_balance_score =
    tpo_count_inside_value_area / max(total_tpo_count, 1)
```

### Scoring Logic

Consensus is high when time, volume, and price cluster around accepted value.

Formula:

```text
consensus_score =
    0.30 * time_inside_value_ratio
  + 0.30 * volume_inside_value_ratio
  + 0.20 * vwap_acceptance_score
  + 0.10 * vwap_reversion_ratio
  + 0.10 * market_profile_balance_score
```

Interpretation:

```text
0.00 - 0.24 = little agreement on value
0.25 - 0.49 = weak or forming consensus
0.50 - 0.74 = moderate accepted value
0.75 - 1.00 = strong balance / high consensus
```

### Confidence Logic

Confidence should be high when the session has enough time and enough profile data.

Inputs:

```text
session_maturity =
    elapsed_session_time / expected_session_duration

profile_completeness =
    min(total_tpo_count / required_tpo_count, 1.0)

data_agreement =
    1.0 - standard_deviation([
        time_inside_value_ratio,
        volume_inside_value_ratio,
        vwap_acceptance_score,
        market_profile_balance_score
    ])
```

Formula:

```text
consensus_confidence =
    0.40 * session_maturity
  + 0.30 * profile_completeness
  + 0.30 * data_agreement
```

### Interpretation

High consensus means the crowd appears to accept value near current structure.

Possible market reading:

- Participants agree on fair value.
- Rotational behavior is more likely than directional repricing.
- A later break from consensus may matter because accepted value was well formed.

### Example Calculation

Inputs:

```text
time_inside_value_ratio = 0.72
volume_inside_value_ratio = 0.78
normalized_vwap_distance = 0.05
vwap_acceptance_score = 1.0 - (0.05 / 0.25) = 0.80
vwap_reversion_ratio = 0.60
market_profile_balance_score = 0.75
```

Score:

```text
consensus_score =
    0.30 * 0.72
  + 0.30 * 0.78
  + 0.20 * 0.80
  + 0.10 * 0.60
  + 0.10 * 0.75

= 0.216 + 0.234 + 0.160 + 0.060 + 0.075
= 0.745
```

Interpretation:

```text
Consensus is moderate-to-strong.
The market appears to be accepting value rather than aggressively repricing.
```

## 2. FOMO Pressure

### Inputs

Required:

```text
normalized_vwap_distance
relative_volume
price_outside_value_area
low_volume_node_break_score
single_print_score
```

Definitions:

```text
price_outside_value_area =
    1.0 if current_price > value_area_high or current_price < value_area_low else 0.0

extension_score =
    min(normalized_vwap_distance / 0.35, 1.0)

relative_volume_score =
    min(relative_volume / 2.0, 1.0)

low_volume_node_break_score =
    1.0 if price moved through nearby low-volume node with range expansion else 0.0

single_print_score =
    single_print_count_recent / max(single_print_count_threshold, 1)
```

### Scoring Logic

FOMO Pressure is high when price extends away from accepted value with expanding participation and poor two-sided auction structure.

Formula:

```text
fomo_pressure_score =
    0.30 * extension_score
  + 0.25 * relative_volume_score
  + 0.20 * price_outside_value_area
  + 0.15 * low_volume_node_break_score
  + 0.10 * single_print_score
```

Interpretation:

```text
0.00 - 0.24 = little chase behavior
0.25 - 0.49 = mild urgency
0.50 - 0.74 = clear chase pressure
0.75 - 1.00 = strong FOMO / emotional extension
```

### Confidence Logic

Confidence should be high when extension, volume, and profile evidence agree.

Inputs:

```text
extension_volume_agreement =
    1.0 - abs(extension_score - relative_volume_score)

profile_confirmation =
    average([
        price_outside_value_area,
        low_volume_node_break_score,
        single_print_score
    ])

session_maturity =
    elapsed_session_time / expected_session_duration
```

Formula:

```text
fomo_pressure_confidence =
    0.40 * extension_volume_agreement
  + 0.35 * profile_confirmation
  + 0.25 * session_maturity
```

### Interpretation

High FOMO Pressure suggests participants may be chasing after price has left accepted value.

Possible market reading:

- Late buyers/sellers may be entering.
- Pullbacks may become shallow if regret is high.
- If acceptance fails, trapped participation risk rises.

### Example Calculation

Inputs:

```text
normalized_vwap_distance = 0.28
extension_score = 0.28 / 0.35 = 0.80
relative_volume = 1.60
relative_volume_score = 1.60 / 2.00 = 0.80
price_outside_value_area = 1.00
low_volume_node_break_score = 0.75
single_print_score = 0.50
```

Score:

```text
fomo_pressure_score =
    0.30 * 0.80
  + 0.25 * 0.80
  + 0.20 * 1.00
  + 0.15 * 0.75
  + 0.10 * 0.50

= 0.240 + 0.200 + 0.200 + 0.1125 + 0.050
= 0.8025
```

Interpretation:

```text
FOMO Pressure is strong.
Price has extended from VWAP, volume is elevated, and profile structure supports chase behavior.
```

## 3. Crowd Fragility

### Inputs

Required:

```text
extension_score
failed_acceptance_score
thin_structure_score
volume_concentration_at_extreme
vwap_reversal_risk
```

Definitions:

```text
extension_score =
    min(normalized_vwap_distance / 0.35, 1.0)

failed_acceptance_score =
    1.0 if price returned inside value after attempting acceptance outside value else 0.0

thin_structure_score =
    low_volume_area_size_near_current_price / max(range, small_number)

volume_concentration_at_extreme =
    volume_at_recent_extreme / max(total_recent_volume, small_number)

vwap_reversal_risk =
    1.0 if price is extended and moving back toward VWAP else 0.0
```

### Scoring Logic

Crowd Fragility is high when participation appears concentrated in a vulnerable area and market structure is thin nearby.

Formula:

```text
crowd_fragility_score =
    0.25 * extension_score
  + 0.25 * failed_acceptance_score
  + 0.20 * thin_structure_score
  + 0.20 * volume_concentration_at_extreme
  + 0.10 * vwap_reversal_risk
```

Interpretation:

```text
0.00 - 0.24 = stable participation
0.25 - 0.49 = mild fragility
0.50 - 0.74 = vulnerable crowd structure
0.75 - 1.00 = highly fragile crowd
```

### Confidence Logic

Confidence should be high when the suspected fragile structure includes both participation and failed acceptance evidence.

Inputs:

```text
trap_evidence =
    average([
        failed_acceptance_score,
        volume_concentration_at_extreme
    ])

structure_evidence =
    average([
        thin_structure_score,
        extension_score
    ])

vwap_confirmation =
    vwap_reversal_risk
```

Formula:

```text
crowd_fragility_confidence =
    0.40 * trap_evidence
  + 0.35 * structure_evidence
  + 0.25 * vwap_confirmation
```

### Interpretation

High Crowd Fragility suggests that the current crowd positioning may be vulnerable to a rapid reversal or liquidation if price moves against them.

Possible market reading:

- Participants may be late or poorly positioned.
- Nearby low-volume structure may create fast movement.
- Failure to accept outside value can turn confidence into stress.

### Example Calculation

Inputs:

```text
extension_score = 0.80
failed_acceptance_score = 1.00
thin_structure_score = 0.65
volume_concentration_at_extreme = 0.70
vwap_reversal_risk = 0.75
```

Score:

```text
crowd_fragility_score =
    0.25 * 0.80
  + 0.25 * 1.00
  + 0.20 * 0.65
  + 0.20 * 0.70
  + 0.10 * 0.75

= 0.200 + 0.250 + 0.130 + 0.140 + 0.075
= 0.795
```

Interpretation:

```text
Crowd Fragility is strong.
The market shows extension, failed acceptance, thin nearby structure, and vulnerable participation near an extreme.
```

## Combined Prototype Output

Example:

```python
BehavioralState:
    symbol = "ES"
    session_id = "2026-05-31"
    timestamp = "2026-05-31T10:45:00-04:00"

    consensus_score = 0.31
    consensus_confidence = 0.64

    fomo_pressure_score = 0.80
    fomo_pressure_confidence = 0.77

    crowd_fragility_score = 0.79
    crowd_fragility_confidence = 0.72

    dominant_state = "FOMO Pressure with high Crowd Fragility"

    evidence = [
        "Price is extended from VWAP.",
        "Relative volume is elevated.",
        "Price moved outside value area.",
        "Nearby low-volume structure increases reversal speed risk.",
        "Failed acceptance would increase trapped participation risk."
    ]

    warnings = [
        "Prototype does not include spread confirmation.",
        "Prototype does not distinguish news-driven repricing from endogenous crowd behavior.",
        "Scores are heuristic and require historical validation."
    ]
```

## Classical Profile Structures as Behavioral Evidence

Classical Market Profile and Volume Profile structures should be treated as behavioral evidence, not automatic trade signals.

Each structure can adjust either:

- A behavioral state score.
- A behavioral state confidence score.
- A narrative explanation.
- A possible transition probability band.

### Poor High

Definition:

A high with little or no excess, often showing repeated TPOs or traded prices at the session high without clear rejection.

Possible behavioral interpretation:

- Buyers may not have completed the auction.
- Sellers may not have meaningfully rejected higher prices.
- The market may be vulnerable to later repair or continuation.

State effects:

```text
Consensus: may decrease confidence if value is balanced but high is unfinished.
FOMO Pressure: may increase if price keeps pressing the poor high.
Fear Pressure: usually neutral.
Conviction: may increase if poor high forms during persistent upside pressure.
Crowd Fragility: may increase if late buyers concentrate near the high.
Regret Potential: may increase for sidelined buyers if high repairs upward.
Belief Acceleration: may increase if repair occurs quickly.
Value Migration: may increase confidence if value follows price higher.
Trapped Participation: may increase if poor high fails and price returns to value.
```

Confidence impact:

- Increases confidence in continuation or repair risk.
- Decreases confidence in completed upside rejection.

Failure modes:

- Poor highs can remain unrepaired for long periods.
- A poor high in low volume may be noise.
- News or settlement flows may distort the structure.

### Poor Low

Definition:

A low with little or no excess, often showing repeated TPOs or traded prices at the session low without clear rejection.

Possible behavioral interpretation:

- Sellers may not have completed the auction.
- Buyers may not have meaningfully rejected lower prices.
- The market may be vulnerable to downside repair.

State effects:

```text
Consensus: may decrease confidence if balanced value has an unfinished low.
FOMO Pressure: usually neutral unless upside chase follows failed repair.
Fear Pressure: may increase if price keeps pressing the poor low.
Conviction: may increase for downside if value migrates lower.
Crowd Fragility: may increase if late shorts concentrate near the low.
Regret Potential: may increase if shorts become trapped after failed repair.
Belief Acceleration: may increase if low repairs quickly.
Value Migration: may increase if lower value is accepted.
Trapped Participation: may increase if poor low fails and price reclaims value.
```

Confidence impact:

- Increases confidence in downside repair risk.
- Decreases confidence in completed downside rejection.

Failure modes:

- Poor lows can remain unresolved.
- Mechanical lows may be caused by time boundaries rather than behavior.
- Thin overnight activity can create misleading poor lows.

### Unfinished Auction

Definition:

An auction that lacks clear excess or rejection at an extreme.

Possible behavioral interpretation:

- The market may not have fully tested participant willingness.
- The extreme may act as an unfinished business area.

State effects:

```text
Consensus: decreases confidence in completed balance.
FOMO Pressure: may increase if participants chase repair.
Fear Pressure: may increase if unfinished downside auction repairs lower.
Conviction: may increase if repair aligns with directional value migration.
Crowd Fragility: increases if many participants are positioned near the unfinished area.
Regret Potential: increases if repair occurs without pullback.
Belief Acceleration: may increase during repair.
Value Migration: increases only if acceptance follows repair.
Trapped Participation: increases if repair fails and reverses.
```

Confidence impact:

- Increases confidence in a possible repair transition.
- Decreases confidence in stable completion.

Failure modes:

- Not all unfinished auctions repair soon.
- Composite profiles may already show excess not visible in session-only view.
- The structure may be irrelevant if higher timeframe context dominates.

### Excess High

Definition:

A high with clear rejection, often shown by a sharp tail, low time at price, and movement away from the high.

Possible behavioral interpretation:

- Buyers tested higher prices and were rejected.
- Sellers found responsive control near the extreme.
- The upside auction may be complete for the current timeframe.

State effects:

```text
Consensus: may increase if price returns to accepted value.
FOMO Pressure: decreases if chase is rejected.
Fear Pressure: may increase for late longs.
Conviction: decreases for upside unless value later migrates higher.
Crowd Fragility: increases if excess follows late upside volume.
Regret Potential: increases for late buyers trapped near the high.
Belief Acceleration: may increase downside after rejection.
Value Migration: decreases unless new lower value forms.
Trapped Participation: increases if high-volume buyers are left above value.
```

Confidence impact:

- Increases confidence in rejection.
- Increases confidence in trapped-long risk when paired with high volume.

Failure modes:

- Excess can be repaired quickly during strong trend days.
- A small tail may not be meaningful.
- Low-liquidity excess can exaggerate rejection.

### Excess Low

Definition:

A low with clear rejection, often shown by a sharp tail, low time at price, and movement away from the low.

Possible behavioral interpretation:

- Sellers tested lower prices and were rejected.
- Buyers found responsive control near the extreme.
- The downside auction may be complete for the current timeframe.

State effects:

```text
Consensus: may increase if price returns to accepted value.
FOMO Pressure: may increase if rejected sellers chase price higher.
Fear Pressure: decreases if downside is rejected.
Conviction: decreases for downside unless lower value later forms.
Crowd Fragility: increases for late shorts.
Regret Potential: increases for trapped shorts and sidelined buyers.
Belief Acceleration: may increase upside after rejection.
Value Migration: increases only if higher value is accepted.
Trapped Participation: increases if high-volume sellers are left below value.
```

Confidence impact:

- Increases confidence in downside rejection.
- Increases confidence in short-trap risk when paired with high volume.

Failure modes:

- Excess lows may be repaired in strong downtrends.
- News-driven spikes may create false excess.
- Overnight excess may not matter during RTH.

### Failed Auction

Definition:

A move beyond a meaningful high, low, value area, or initial balance that fails to gain acceptance and returns back inside prior structure.

Possible behavioral interpretation:

- Breakout participants may be trapped.
- The crowd tested a new belief and rejected it.
- The market may transition from continuation to reversal or rotation.

State effects:

```text
Consensus: may increase if price returns to prior value.
FOMO Pressure: decreases after failure.
Fear Pressure: increases against failed breakout participants.
Conviction: decreases in the failed direction.
Crowd Fragility: increases strongly.
Regret Potential: increases.
Belief Acceleration: may increase opposite the failed move.
Value Migration: decreases in failed direction.
Trapped Participation: increases strongly.
```

Confidence impact:

- Strongly increases confidence in trapped participation.
- Increases confidence in reversal/rotation transition.

Failure modes:

- A failed auction can become a deeper retest before continuation.
- Failure may be temporary during volatile sessions.
- Requires clear acceptance criteria.

### Single Prints

Definition:

Market Profile areas with only one TPO print, often indicating fast directional movement and limited two-sided trade.

Possible behavioral interpretation:

- Participants moved urgently through price.
- The auction may have left emotional or low-acceptance structure.
- Single prints can act as future repair zones.

State effects:

```text
Consensus: decreases in the single-print zone.
FOMO Pressure: increases if single prints occur upward.
Fear Pressure: increases if single prints occur downward.
Conviction: increases if single prints hold and value migrates.
Crowd Fragility: increases if price returns toward the single prints.
Regret Potential: increases for participants left behind.
Belief Acceleration: increases.
Value Migration: increases only if acceptance follows.
Trapped Participation: increases if single-print move fails.
```

Confidence impact:

- Increases confidence in emotional movement.
- Decreases confidence in accepted value within the single-print zone.

Failure modes:

- Strong trends can leave single prints that do not repair quickly.
- Thin sessions can create false single prints.
- Data resolution can distort TPO structure.

### Double Distribution

Definition:

A profile with two distinct accepted value areas separated by a low-volume or low-time area.

Possible behavioral interpretation:

- The market transitioned from one belief zone to another.
- Participants accepted a new area after rejecting or leaving the prior one.

State effects:

```text
Consensus: may be high within each distribution but low between them.
FOMO Pressure: may increase during transition between distributions.
Fear Pressure: may increase during downside transition.
Conviction: increases if second distribution holds.
Crowd Fragility: increases near the low-volume separation zone.
Regret Potential: increases for participants anchored to the old distribution.
Belief Acceleration: increases during transition.
Value Migration: increases strongly.
Trapped Participation: may increase if second distribution fails.
```

Confidence impact:

- Increases confidence in value migration if second distribution persists.
- Increases confidence in transition-zone importance.

Failure modes:

- Two distributions may merge later.
- Lunch-hour or low-volume periods can create misleading separation.
- Requires session context.

### P-Shaped Profile

Definition:

A profile shaped like a capital P, often with a narrow lower stem and broader upper distribution.

Possible behavioral interpretation:

- Short covering or upside liquidation may have occurred.
- Higher prices were later accepted, but the origin may be less stable.

State effects:

```text
Consensus: may increase in upper distribution.
FOMO Pressure: may increase during the stem.
Fear Pressure: may decrease after shorts cover.
Conviction: mixed; depends on whether upper value holds.
Crowd Fragility: increases if upper distribution lacks true buying.
Regret Potential: increases for shorts.
Belief Acceleration: increases during stem formation.
Value Migration: increases if upper distribution accepts.
Trapped Participation: increases for shorts if price holds higher.
```

Confidence impact:

- Increases confidence in short-covering hypothesis.
- Increases confidence in upper value only if time and volume build there.

Failure modes:

- P-shape can also occur in legitimate accumulation.
- Requires volume and time confirmation.
- Shape labels can be subjective.

### b-Shaped Profile

Definition:

A profile shaped like a lowercase b, often with a narrow upper stem and broader lower distribution.

Possible behavioral interpretation:

- Long liquidation may have occurred.
- Lower prices were later accepted, but the origin may be emotionally driven.

State effects:

```text
Consensus: may increase in lower distribution.
FOMO Pressure: usually decreases unless downside chase continues.
Fear Pressure: increases during the stem.
Conviction: mixed; depends on whether lower value holds.
Crowd Fragility: increases if lower distribution lacks durable selling.
Regret Potential: increases for longs.
Belief Acceleration: increases during downside stem formation.
Value Migration: increases if lower distribution accepts.
Trapped Participation: increases for longs if price holds lower.
```

Confidence impact:

- Increases confidence in long-liquidation hypothesis.
- Increases confidence in lower value only if time and volume build there.

Failure modes:

- b-shape can also occur in legitimate distribution.
- Requires context around prior positioning.
- Shape alone is insufficient.

### Value Area Migration

Definition:

Movement of the accepted value area higher or lower over time.

Possible behavioral interpretation:

- Collective belief is shifting.
- Participants are accepting a new reference zone.

State effects:

```text
Consensus: increases if new value stabilizes.
FOMO Pressure: may increase during migration.
Fear Pressure: may increase during downside migration.
Conviction: increases when migration aligns with VWAP and volume.
Crowd Fragility: decreases if migration is accepted; increases if it fails.
Regret Potential: increases for participants anchored to old value.
Belief Acceleration: increases if migration speed rises.
Value Migration: increases strongly.
Trapped Participation: increases if migration fails.
```

Confidence impact:

- Strongly increases confidence in Value Migration.
- Increases Conviction confidence when supported by VWAP and volume.

Failure modes:

- Early-session value areas are unstable.
- Migration can reverse after news.
- Low-volume drift can mimic migration.

### POC Migration

Definition:

Movement of Point of Control from one price level to another.

Possible behavioral interpretation:

- Participation is concentrating at a new price.
- The crowd may be changing its accepted reference point.

State effects:

```text
Consensus: increases near new POC if stable.
FOMO Pressure: may increase if POC chases price.
Fear Pressure: may increase if POC migrates lower quickly.
Conviction: increases if POC migration aligns with direction.
Crowd Fragility: decreases if POC stabilizes; increases if price rejects it.
Regret Potential: increases around old POC abandonment.
Belief Acceleration: increases if POC shifts rapidly.
Value Migration: increases.
Trapped Participation: increases if new POC fails.
```

Confidence impact:

- Increases confidence in accepted participation shift.
- Stronger when supported by value area migration.

Failure modes:

- POC can jump mechanically in immature profiles.
- POC migration can lag price.
- High-volume events can distort POC.

### Initial Balance Breakout/Failure

Definition:

A move outside the initial balance range that either gains acceptance or fails and returns inside.

Possible behavioral interpretation:

- Breakout acceptance may indicate directional discovery.
- Breakout failure may indicate trapped participants and rejected belief.

State effects:

```text
Consensus: decreases during accepted breakout; increases if failure returns to balance.
FOMO Pressure: increases on accepted breakout with volume.
Fear Pressure: increases on downside break or failed upside break.
Conviction: increases if breakout holds and value migrates.
Crowd Fragility: increases if breakout fails.
Regret Potential: increases for missed accepted breakouts or trapped failed ones.
Belief Acceleration: increases on fast breakout.
Value Migration: increases if new value forms outside IB.
Trapped Participation: increases on failed IB breakout.
```

Confidence impact:

- Accepted IB breakout increases confidence in continuation/value migration.
- Failed IB breakout increases confidence in trapped participation.

Failure modes:

- Initial balance definitions vary by market.
- False breaks are common during volatile opens.
- Overnight inventory can distort RTH IB behavior.

### Incomplete Auction

Definition:

An auction with insufficient evidence of completion, often overlapping with poor highs/lows or unfinished extremes.

Possible behavioral interpretation:

- Market may need more information or further testing.
- Participants have not clearly rejected the extreme.

State effects:

```text
Consensus: decreases confidence in completed balance.
FOMO Pressure: may increase if participants pursue completion higher.
Fear Pressure: may increase if participants pursue completion lower.
Conviction: increases only if completion aligns with accepted direction.
Crowd Fragility: increases near incomplete extremes.
Regret Potential: increases if completion occurs quickly.
Belief Acceleration: may increase during repair.
Value Migration: increases only if repaired area accepts.
Trapped Participation: increases if repair fails.
```

Confidence impact:

- Increases confidence in repair probability.
- Decreases confidence in finality of the current extreme.

Failure modes:

- Incomplete auctions can remain incomplete.
- Higher timeframe profile may show completion.
- Data granularity may mislabel completion.

## Immature Profile Handling

Early-session and incomplete profiles should reduce confidence.

Profile maturity inputs:

```text
elapsed_session_time
total_tpo_count
total_session_volume
value_area_defined
volume_distribution_depth
initial_balance_complete
```

Rules:

- Early session: reduce all profile-dependent confidence scores.
- Incomplete value area: avoid strong Consensus or Value Migration conclusions.
- Insufficient TPO count: reduce Market Profile evidence weight.
- Insufficient volume distribution: reduce Volume Profile evidence weight.
- Initial balance not complete: avoid strong IB breakout/failure conclusions.

Suggested maturity formula:

```text
profile_maturity =
    0.30 * elapsed_session_ratio
  + 0.25 * min(total_tpo_count / required_tpo_count, 1.0)
  + 0.25 * min(total_session_volume / required_session_volume, 1.0)
  + 0.20 * value_area_defined_flag
```

Confidence adjustment:

```text
adjusted_confidence =
    raw_confidence * profile_maturity
```

Interpretation:

```text
profile_maturity < 0.40:
    Use cautious language. Profile is immature.

profile_maturity 0.40-0.70:
    Use moderate confidence only.

profile_maturity > 0.70:
    Profile evidence can be weighted normally.
```

## Session Separation

The analyzer should distinguish profile sources.

### RTH Profile

Regular trading hours profile.

Use for:

- Intraday decision context.
- Initial balance.
- RTH value acceptance.
- RTH VWAP relationship.

### ETH / Overnight Profile

Extended or overnight profile.

Use for:

- Overnight inventory.
- Globex high/low context.
- Pre-RTH value references.
- Gaps between overnight value and RTH open.

### Prior Day Profile

Previous regular session profile.

Use for:

- Prior value area.
- Prior POC.
- Prior excess or poor extremes.
- Current session acceptance/rejection relative to yesterday's value.

### Composite Profile

Multi-session profile.

Use for:

- Higher timeframe accepted value.
- Major high-volume nodes.
- Major low-volume transition zones.
- Broader consensus or migration.

### When To Compare Current Session Against Prior Session

Compare current RTH against prior RTH when:

- Price opens inside prior value.
- Price opens outside prior value and attempts acceptance.
- Current POC migrates toward or away from prior POC.
- Current value overlaps, separates from, or rejects prior value.
- Current session repairs prior poor high/low.
- Current session tests prior excess.

Suggested comparison flags:

```text
inside_prior_value
above_prior_value
below_prior_value
accepted_outside_prior_value
failed_outside_prior_value
overlapping_value
separate_value
prior_poc_retested
prior_extreme_repaired
```

## Output Narrative

The analyzer should produce a final summary paragraph.

The summary should:

- Explain the dominant behavioral state.
- Mention the strongest evidence.
- Mention confidence and profile maturity when relevant.
- Estimate possible behavioral state transitions.
- Avoid direct trade recommendations.

Required safety of language:

```text
The current structure suggests increased probability of continuation/reversal/rotation/repricing, but not a trade recommendation.
```

Example:

```text
The current structure shows moderate FOMO Pressure with elevated Crowd Fragility.
Price is extended from VWAP, volume expanded outside value, and the profile left
thin structure below the recent high. This suggests increased probability of
either continuation if value migrates higher, or reversal/failed auction repair
if price returns back through the low-volume area. This is not a trade
recommendation.
```

## Movement Probability Framework

The analyzer should not issue direct trade calls.

It may estimate probability bands for possible next behavioral transitions.

Probability bands:

```text
low
moderate
elevated
high
```

Transition categories:

```text
continuation
reversal
rotation
value migration
liquidation
failed auction repair
```

Example mapping:

```text
High Consensus + mature balanced profile:
    rotation = elevated
    continuation = low/moderate
    value migration = moderate if near edge of value

High FOMO Pressure + accepted value migration:
    continuation = elevated
    value migration = elevated
    reversal = moderate

High FOMO Pressure + failed auction:
    reversal = elevated
    failed auction repair = high
    trapped participation = elevated

High Crowd Fragility + thin structure + failed acceptance:
    reversal = elevated
    liquidation = moderate/high
    continuation = low unless value re-accepts
```

Output example:

```python
transition_probabilities = {
    "continuation": "moderate",
    "reversal": "elevated",
    "rotation": "moderate",
    "value_migration": "low",
    "liquidation": "moderate",
    "failed_auction_repair": "elevated",
}
```

## Point & Figure as Behavioral Evidence

Point & Figure should be considered later as a conviction filter.

Design notes:

- P&F removes time noise and focuses on meaningful directional price movement.
- P&F columns may help distinguish real directional commitment from noisy rotation.
- P&F breakouts can be used as supporting evidence, not standalone signals.
- P&F reversal counts may help identify weakening conviction.
- P&F should not replace Market Profile, Volume Profile, VWAP, or volume evidence.

Possible future uses:

```text
Conviction filter:
    Directional P&F breakout supports Conviction if VWAP and value migration agree.

Fragility filter:
    Failed P&F breakout plus failed auction increases Crowd Fragility confidence.

Noise filter:
    If profile suggests movement but P&F remains rotational, reduce Belief Acceleration confidence.
```

Failure modes:

- Box size and reversal settings can change conclusions.
- P&F may lag fast auction changes.
- P&F ignores time, so it must be paired with profile acceptance.
- P&F breakouts can fail in low-liquidity conditions.

## Prototype Processing Flow

```text
Chart Data
    |
    v
Normalize Inputs
    |
    v
Compute Consensus
    |
    v
Compute FOMO Pressure
    |
    v
Compute Crowd Fragility
    |
    v
Compute Confidence Scores
    |
    v
Generate Evidence Notes
    |
    v
BehavioralState Output
```

## Required Validation Dataset

The first validation dataset should include labeled examples of:

- Balanced sessions.
- Trend days.
- Failed breakouts.
- Failed breakdowns.
- VWAP reclaim days.
- VWAP loss days.
- High-volume reversals.
- Low-volume drift sessions.

Each example should include:

```text
price bars
volume bars
VWAP history
Volume Profile
Market Profile
manual human label
post-session notes
```

## Prototype Non-Goals

- No spread relationships yet.
- No portfolio logic.
- No automated trade signals.
- No stop/target generation.
- No autonomous execution.
- No claim of predictive certainty.
- No replacement for human review.

## Open Questions

1. What thresholds should define VWAP extension by product?
2. Should formulas normalize by ATR, session range, or recent realized volatility?
3. How should early-session data be handled when profiles are immature?
4. How should news-driven moves be labeled?
5. How should overnight and regular sessions be separated?
6. Should Market Profile single prints carry more weight than Volume Profile low-volume nodes?
7. How many historical examples are needed before trusting the heuristic weights?
8. Should scores be recalculated every bar, every profile update, or only at decision points?
