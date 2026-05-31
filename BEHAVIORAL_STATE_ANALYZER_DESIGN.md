# Behavioral State Analyzer Design

## Objective

Define the mathematical and observational framework for a future `BehavioralStateAnalyzer`.

The analyzer should estimate behavioral market states from observable market structure: price, time, volume, VWAP, Volume Profile, Market Profile, and spread relationships.

This is a design-only document. It does not define final trading signals or implementation code.

## General Scoring Model

Each behavioral state can be represented as:

```text
state_score = weighted_sum(normalized_proxies)
confidence = evidence_quality * proxy_agreement * data_completeness
```

Suggested score range:

```text
0.00 = absent
0.25 = weak
0.50 = moderate
0.75 = strong
1.00 = extreme
```

Suggested confidence range:

```text
0.00 = no confidence
0.25 = low confidence
0.50 = moderate confidence
0.75 = high confidence
1.00 = very high confidence
```

The analyzer should separate:

- State intensity: how much the state appears present.
- Confidence: how reliable the evidence is.
- Evidence notes: why the analyzer scored the state that way.

## Shared Inputs

Potential common inputs:

```text
price
price_change
price_velocity
range_extension
volume
relative_volume
time_at_price
time_above_vwap
time_below_vwap
vwap
vwap_slope
distance_from_vwap
volume_profile_poc
value_area_high
value_area_low
high_volume_nodes
low_volume_nodes
market_profile_tpos
single_prints
initial_balance_high
initial_balance_low
spread_change
spread_divergence
```

Normalization examples:

```text
normalized_distance_from_vwap = abs(price - vwap) / atr
normalized_volume = current_volume / average_volume
normalized_velocity = abs(price_change) / average_price_change
value_area_distance = distance_from_value_area / atr
```

## 1. Consensus

### Definition

Consensus is the degree to which market participants appear to agree on value.

High consensus suggests acceptance, balance, and repeated participation near similar prices. Low consensus suggests disagreement, rejection, transition, or active repricing.

### Observable Proxies

- Time spent near Point of Control.
- Volume concentration inside value area.
- Narrowing range.
- Repeated VWAP reversion.
- Balanced Market Profile structure.
- Low directional price velocity.
- Stable spread relationships.

### Candidate Formula Inputs

```text
time_acceptance_score =
    time_inside_value_area / total_session_time

volume_acceptance_score =
    volume_inside_value_area / total_session_volume

vwap_reversion_score =
    count_successful_reversions_to_vwap / total_vwap_tests

range_compression_score =
    1 - current_range / average_session_range

consensus =
    0.30 * time_acceptance_score
  + 0.30 * volume_acceptance_score
  + 0.20 * vwap_reversion_score
  + 0.20 * range_compression_score
```

### Confidence Score Method

Increase confidence when:

- Time and volume agree.
- Session has enough elapsed time.
- Value area is well formed.
- Profile shape is balanced.

Decrease confidence when:

- Data is early-session only.
- News shock is active.
- Volume is abnormally low.
- Profile is incomplete.

### Expected State Transitions

Potential transitions:

```text
consensus -> value migration
consensus -> FOMO pressure
consensus -> fear pressure
consensus -> crowd fragility
```

Interpretation:

- Long consensus can precede directional expansion.
- Consensus near extremes can become fragile if participation is crowded.

### Failure Modes

- Mistaking low volatility for true agreement.
- Ignoring hidden positioning.
- Treating holiday/low-volume sessions as consensus.
- Missing external catalysts.

### Historical Examples

- Multi-day balance before a breakout.
- Narrow range day around VWAP before trend day.
- Index futures balancing ahead of a central bank announcement.
- Commodity market consolidating near high-volume node before repricing.

## 2. FOMO Pressure

### Definition

FOMO pressure is the urgency to participate after price has already moved.

It reflects chase behavior, late entries, and fear of missing further movement.

### Observable Proxies

- Price extension away from VWAP.
- Increasing volume after breakout.
- Low pullback depth.
- Rapid movement through low-volume nodes.
- Price holding outside prior value.
- Market Profile single prints.
- Spread confirmation after outright movement.

### Candidate Formula Inputs

```text
extension_score =
    min(abs(price - vwap) / atr, cap) / cap

late_volume_score =
    volume_after_breakout / average_breakout_volume

pullback_shallowness_score =
    1 - pullback_depth / prior_impulse_range

lvn_acceleration_score =
    price_velocity_through_lvn / average_velocity

fomo_pressure =
    0.30 * extension_score
  + 0.25 * late_volume_score
  + 0.20 * pullback_shallowness_score
  + 0.25 * lvn_acceleration_score
```

### Confidence Score Method

Increase confidence when:

- Price extension, volume expansion, and shallow pullbacks align.
- Movement occurs after a clear breakout.
- Price remains accepted outside prior value.

Decrease confidence when:

- Volume is not expanding.
- Spread relationships do not confirm.
- Move occurs in low-liquidity conditions.
- Price immediately returns to value.

### Expected State Transitions

Potential transitions:

```text
FOMO pressure -> conviction
FOMO pressure -> trapped participation
FOMO pressure -> regret potential
FOMO pressure -> crowd fragility
```

Interpretation:

- FOMO can mature into conviction if value migrates.
- FOMO can become trapped participation if breakout fails.

### Failure Modes

- Confusing institutional repricing with retail chase.
- Treating normal trend continuation as emotional FOMO.
- Overweighting price extension without volume confirmation.
- Ignoring volatility regime.

### Historical Examples

- Breakout from a multi-day balance with late volume surge.
- Equity index rally after major resistance clears.
- Commodity spike through low-volume profile area.
- Short-covering rally that becomes a chase.

## 3. Fear Pressure

### Definition

Fear pressure is the urgency to exit, hedge, liquidate, or avoid risk.

It often appears as rapid downside movement, failed recovery, and participation that prioritizes immediacy over price.

### Observable Proxies

- Fast downside price velocity.
- VWAP loss and failed reclaim.
- Expanding volume on downside movement.
- Thin profile below value.
- Break through prior value area low.
- Spread stress or divergence.
- Market Profile poor structure or single prints.

### Candidate Formula Inputs

```text
downside_velocity_score =
    downside_price_velocity / average_downside_velocity

vwap_failure_score =
    failed_vwap_reclaims / vwap_reclaim_attempts

liquidation_volume_score =
    downside_volume / average_downside_volume

value_loss_score =
    distance_below_value_area_low / atr

fear_pressure =
    0.30 * downside_velocity_score
  + 0.25 * vwap_failure_score
  + 0.25 * liquidation_volume_score
  + 0.20 * value_loss_score
```

### Confidence Score Method

Increase confidence when:

- Downside velocity and volume expand together.
- VWAP reclaim attempts fail.
- Price accepts below prior value.
- Related spreads confirm stress.

Decrease confidence when:

- Move is headline-driven and immediately reverses.
- Volume is thin.
- Downside move occurs into strong known support.
- Spread relationships diverge positively.

### Expected State Transitions

Potential transitions:

```text
fear pressure -> liquidation
fear pressure -> trapped participation
fear pressure -> regret potential
fear pressure -> consensus at lower value
```

Interpretation:

- Fear can resolve into liquidation.
- After liquidation, price may discover lower value or violently mean-revert.

### Failure Modes

- Mistaking normal pullback for fear.
- Overweighting one large bar.
- Ignoring scheduled event volatility.
- Missing absorption by stronger participants.

### Historical Examples

- Index futures selling through prior value after failed VWAP reclaim.
- Commodity liquidation after inventory surprise.
- Equity market risk-off move with expanding downside volume.
- Failed breakout that reverses into stop-driven selling.

## 4. Conviction

### Definition

Conviction is persistent directional participation supported by price, time, volume, and value migration.

It is stronger than momentum because it implies acceptance and continued participation, not only speed.

### Observable Proxies

- Price holding above/below VWAP.
- VWAP slope aligned with direction.
- Pullbacks absorbed near value.
- Point of Control migration.
- Value Area migration.
- Higher highs/lows or lower highs/lows.
- Volume confirms movement.

### Candidate Formula Inputs

```text
vwap_alignment_score =
    time_on_directional_side_of_vwap / total_session_time

vwap_slope_score =
    directional_vwap_slope / average_abs_vwap_slope

value_migration_score =
    directional_change_in_poc / atr

pullback_absorption_score =
    successful_directional_resumptions / pullback_count

conviction =
    0.30 * vwap_alignment_score
  + 0.20 * vwap_slope_score
  + 0.30 * value_migration_score
  + 0.20 * pullback_absorption_score
```

### Confidence Score Method

Increase confidence when:

- VWAP slope, price location, and value migration agree.
- Pullbacks are bought/sold consistently.
- Volume confirms direction.

Decrease confidence when:

- Price moves but value does not migrate.
- Volume is weak.
- Movement is only through thin liquidity.
- Spread relationships do not confirm.

### Expected State Transitions

Potential transitions:

```text
conviction -> consensus at new value
conviction -> FOMO pressure
conviction -> exhaustion
conviction -> crowd fragility
```

Interpretation:

- Conviction can create new value.
- Extreme conviction can attract late participation and become fragile.

### Failure Modes

- Confusing short covering with durable conviction.
- Ignoring lack of value migration.
- Treating one-way price movement as accepted value.
- Missing absorption failure.

### Historical Examples

- Trend day with persistent VWAP separation.
- Multi-session value migration higher/lower.
- Commodity trend confirmed by calendar spreads.
- Equity index rally with rising POC and shallow pullbacks.

## 5. Crowd Fragility

### Definition

Crowd fragility is the market's susceptibility to rapid repositioning.

A fragile crowd may look confident on the surface but has poor structural support if price moves against the dominant positioning.

### Observable Proxies

- Heavy volume near vulnerable extremes.
- Price far from accepted value.
- Thin volume below longs or above shorts.
- Failed breakout after participation surge.
- VWAP distance extreme.
- Spread divergence.
- High regret potential.

### Candidate Formula Inputs

```text
positioning_concentration_score =
    volume_at_failed_extreme / total_recent_volume

thin_structure_score =
    low_volume_area_size_nearby / atr

extension_score =
    abs(price - vwap) / atr

failed_acceptance_score =
    failed_acceptance_events / breakout_attempts

crowd_fragility =
    0.30 * positioning_concentration_score
  + 0.25 * thin_structure_score
  + 0.20 * extension_score
  + 0.25 * failed_acceptance_score
```

### Confidence Score Method

Increase confidence when:

- Heavy participation appears near a failed level.
- Nearby structure is thin.
- Price is extended from VWAP or value.
- Related markets diverge.

Decrease confidence when:

- Value has migrated and accepted the new level.
- Pullbacks are absorbed cleanly.
- Volume confirms healthy continuation.
- Volatility regime explains extension.

### Expected State Transitions

Potential transitions:

```text
crowd fragility -> trapped participation
crowd fragility -> fear pressure
crowd fragility -> regret potential
crowd fragility -> renewed conviction
```

Interpretation:

- Fragility can break into forced repositioning.
- Fragility can resolve harmlessly if new value is accepted.

### Failure Modes

- Calling every extension fragile.
- Ignoring valid trend-day structure.
- Misreading high volume as trapped rather than accepted.
- Missing broader timeframe support.

### Historical Examples

- Failed upside breakout with high volume and quick return to value.
- Parabolic commodity move before liquidation.
- Crowded equity index rally into failed acceptance.
- Spread divergence before outright reversal.

## 6. Regret Potential

### Definition

Regret potential is the likelihood that participants will feel forced to re-enter, exit, chase, or reverse after being wrong-footed.

It is the emotional fuel created by missed opportunity or incorrect participation.

### Observable Proxies

- Breakout from long balance.
- Failed return to prior value.
- Rapid move after low participation.
- Reclaim/loss of VWAP after failed move.
- Trapped volume zones.
- Price moving away before late participants can enter.

### Candidate Formula Inputs

```text
missed_move_score =
    directional_range_after_breakout / atr

balance_duration_score =
    balance_duration / average_balance_duration

failed_reentry_score =
    failed_pullback_entries / pullback_attempts

trapped_zone_score =
    volume_in_wrong_footed_area / total_recent_volume

regret_potential =
    0.25 * missed_move_score
  + 0.25 * balance_duration_score
  + 0.20 * failed_reentry_score
  + 0.30 * trapped_zone_score
```

### Confidence Score Method

Increase confidence when:

- Move begins from clear balance.
- Pullbacks fail to offer easy entry.
- Prior participants are visibly trapped.
- Price accepts away from prior value.

Decrease confidence when:

- Move lacks participation.
- Price quickly returns to balance.
- Breakout occurs during illiquid period.
- No clear prior consensus zone exists.

### Expected State Transitions

Potential transitions:

```text
regret potential -> FOMO pressure
regret potential -> conviction
regret potential -> trapped participation
regret potential -> consensus at new value
```

Interpretation:

- Regret can become chase.
- If price accepts, regret helps reinforce new value.

### Failure Modes

- Inferring regret without a clear group of missed/trapped participants.
- Overweighting price movement alone.
- Ignoring higher timeframe levels.
- Treating every breakout as regret-producing.

### Historical Examples

- Breakout from multi-day balance that never retests entry.
- Failed pullback after VWAP reclaim.
- Short squeeze after failed breakdown.
- Trend day where late participants chase shallow pullbacks.

## 7. Belief Acceleration

### Definition

Belief acceleration is the rate at which collective market belief appears to be changing.

It captures fast repricing, not merely price movement.

### Observable Proxies

- Increasing price velocity.
- Increasing volume.
- VWAP slope change.
- POC or value area migration.
- Spread repricing.
- Faster rotations in one direction.

### Candidate Formula Inputs

```text
price_acceleration_score =
    current_price_velocity / prior_price_velocity

volume_acceleration_score =
    current_relative_volume / prior_relative_volume

vwap_slope_change_score =
    current_vwap_slope - prior_vwap_slope

value_migration_velocity_score =
    current_poc_change_rate / prior_poc_change_rate

belief_acceleration =
    0.30 * price_acceleration_score
  + 0.20 * volume_acceleration_score
  + 0.25 * vwap_slope_change_score
  + 0.25 * value_migration_velocity_score
```

### Confidence Score Method

Increase confidence when:

- Price, volume, VWAP, and value migration accelerate together.
- Related spreads confirm repricing.
- Acceleration persists beyond one bar.

Decrease confidence when:

- Acceleration is only price-based.
- Move is a single liquidation bar.
- VWAP and value do not respond.
- Data frequency is too low.

### Expected State Transitions

Potential transitions:

```text
belief acceleration -> conviction
belief acceleration -> FOMO pressure
belief acceleration -> fear pressure
belief acceleration -> exhaustion
```

Interpretation:

- Upside acceleration can become conviction or FOMO.
- Downside acceleration can become fear or liquidation.

### Failure Modes

- Mistaking volatility spikes for belief change.
- Overreacting to isolated large trades.
- Ignoring event-driven repricing.
- Using insufficient smoothing.

### Historical Examples

- Fed announcement repricing across index futures.
- Commodity breakout with accelerating volume and spreads.
- Equity reversal where VWAP slope flips sharply.
- Fast migration from one value area to another.

## 8. Value Migration

### Definition

Value migration is the movement of accepted value from one price area to another.

It indicates that the crowd is not only moving price but beginning to accept a new reference zone.

### Observable Proxies

- Point of Control shifts.
- Value Area High/Low shifts.
- Time acceptance in new area.
- VWAP slope and location.
- High-volume node formation.
- Failed return to old value.

### Candidate Formula Inputs

```text
poc_shift_score =
    abs(current_poc - prior_poc) / atr

value_area_shift_score =
    abs(current_value_midpoint - prior_value_midpoint) / atr

new_area_acceptance_score =
    time_in_new_value_area / total_recent_time

old_value_rejection_score =
    failed_returns_to_prior_value / return_attempts

value_migration =
    0.30 * poc_shift_score
  + 0.25 * value_area_shift_score
  + 0.25 * new_area_acceptance_score
  + 0.20 * old_value_rejection_score
```

### Confidence Score Method

Increase confidence when:

- POC and value area shift together.
- Time and volume build in the new area.
- Old value is rejected.
- VWAP follows the migration.

Decrease confidence when:

- Price moves but value does not.
- New area has low volume.
- Migration is only intrabar.
- Prior value keeps attracting price.

### Expected State Transitions

Potential transitions:

```text
value migration -> conviction
value migration -> consensus
value migration -> FOMO pressure
value migration -> trapped participation
```

Interpretation:

- Accepted migration supports conviction.
- Failed migration can trap participants.

### Failure Modes

- Mistaking temporary price movement for value change.
- Overweighting early-session POC shifts.
- Ignoring session boundaries.
- Treating low-volume drift as migration.

### Historical Examples

- Trend day with POC migration in direction of trade.
- Multi-session acceptance above prior value.
- Failed migration above value leading to reversal.
- Commodity market repricing to a higher value band.

## 9. Trapped Participation

### Definition

Trapped participation describes participants who entered or held positions at prices that become structurally unfavorable.

These participants may later become forced buyers or sellers.

### Observable Proxies

- High volume at failed breakout/breakdown.
- Price returning through a high-participation zone.
- Failed acceptance outside value.
- VWAP reclaim/loss after heavy participation.
- Poor continuation after volume surge.
- Spread reversal after crowded movement.

### Candidate Formula Inputs

```text
failed_breakout_volume_score =
    volume_at_failed_breakout / average_breakout_volume

return_through_zone_score =
    speed_of_return_through_participation_zone / average_speed

failed_acceptance_score =
    time_outside_value_before_return / expected_acceptance_time

vwap_reversal_score =
    vwap_reclaim_or_loss_after_volume_surge

trapped_participation =
    0.35 * failed_breakout_volume_score
  + 0.25 * return_through_zone_score
  + 0.20 * failed_acceptance_score
  + 0.20 * vwap_reversal_score
```

### Confidence Score Method

Increase confidence when:

- High volume occurred at the failed level.
- Price quickly returns through the participation zone.
- VWAP confirms reversal.
- Related spreads reverse or fail to confirm.

Decrease confidence when:

- Volume at the level was low.
- Price returns slowly and constructively.
- New value forms nearby.
- Higher timeframe trend still supports the move.

### Expected State Transitions

Potential transitions:

```text
trapped participation -> fear pressure
trapped participation -> regret potential
trapped participation -> liquidation
trapped participation -> renewed consensus
```

Interpretation:

- Trapped longs can fuel downside.
- Trapped shorts can fuel upside.
- If price stabilizes, trapped participation may be absorbed.

### Failure Modes

- Assuming all failed moves create meaningful traps.
- Missing absorption by larger participants.
- Ignoring whether trapped participants are leveraged.
- Treating high volume as wrong-sided without confirmation.

### Historical Examples

- Failed breakout above prior value with high volume and fast return.
- Failed breakdown below VWAP followed by short squeeze.
- Commodity spike through resistance followed by liquidation.
- Equity index reclaim after heavy downside volume traps shorts.

## Cross-State Interpretation

The analyzer should not treat states as isolated. Many states interact.

Examples:

```text
consensus + low fragility
  -> stable balance

consensus + high fragility
  -> vulnerable balance

FOMO pressure + value migration
  -> possible conviction

FOMO pressure + failed acceptance
  -> trapped participation

fear pressure + high trapped participation
  -> liquidation risk

conviction + rising regret potential
  -> trend continuation risk for sidelined participants
```

## Future Analyzer Output

Possible output shape:

```python
BehavioralStateReport:
    consensus: StateScore
    fomo_pressure: StateScore
    fear_pressure: StateScore
    conviction: StateScore
    crowd_fragility: StateScore
    regret_potential: StateScore
    belief_acceleration: StateScore
    value_migration: StateScore
    trapped_participation: StateScore
    dominant_state: str
    likely_transitions: list[str]
    evidence: list[str]
    warnings: list[str]
```

Where:

```python
StateScore:
    value: float
    confidence: float
    evidence: list[str]
    failure_modes: list[str]
```

## Non-Goals

- No autonomous trade decisions.
- No order generation.
- No claim of predictive certainty.
- No portfolio sizing.
- No replacement for risk management.
- No medical, legal, or financial advice framing.
