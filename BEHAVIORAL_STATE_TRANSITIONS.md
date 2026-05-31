# Behavioral State Transitions Design

## Objective

Design the transition model that sits above `BehavioralStateAnalyzer`.

The analyzer estimates the current behavioral state. The transition model estimates likely next behavioral states.

The goal is not trade signals. The goal is weather-style behavioral forecasting:

```text
Given the current market structure, what behavioral states are becoming more or less likely next?
```

The model should express:

- Probable next states.
- Confidence in the transition estimate.
- Evidence supporting the transition.
- Failure modes and uncertainty.

## Behavioral States

The transition model uses the existing behavioral states:

- Consensus
- Belief Acceleration
- Conviction
- FOMO Pressure
- Fear Pressure
- Crowd Fragility
- Regret Potential
- Value Migration
- Trapped Participation

## Core Transition Framework

Primary behavioral arc:

```text
Consensus
    |
    v
Belief Acceleration
    |
    v
Conviction
    |
    v
FOMO Pressure
    |
    v
Crowd Fragility
    |
    v
Fear Pressure
    |
    v
New Consensus
```

This is not a fixed sequence. It is a common path from balance to repricing, crowding, stress, and renewed balance.

Alternative pathways:

```text
Consensus -> Failed Auction -> Rotation -> Consensus

Consensus -> Belief Acceleration -> Failed Acceptance -> Trapped Participation -> Fear Pressure

Conviction -> Value Migration -> New Consensus

FOMO Pressure -> Value Migration -> Conviction

FOMO Pressure -> Failed Auction -> Trapped Participation -> Reversal

Fear Pressure -> Liquidation -> Excess Low -> New Consensus

Crowd Fragility -> Absorption -> Renewed Conviction

Regret Potential -> FOMO Pressure -> Conviction
```

## Transition Probability Concepts

Transition probability should be expressed in bands rather than precise predictions:

```text
low
moderate
elevated
high
```

Example output:

```python
TransitionForecast:
    current_state = "Consensus"
    likely_next_states = [
        {"state": "Belief Acceleration", "probability": "elevated", "confidence": 0.68},
        {"state": "Rotation", "probability": "moderate", "confidence": 0.61},
        {"state": "Failed Auction", "probability": "low", "confidence": 0.42},
    ]
```

Probability should reflect directional likelihood of behavioral transition, not trade outcome.

## Transition Confidence Concepts

Confidence should be separate from probability.

Example:

```text
Probability:
    Belief Acceleration is elevated.

Confidence:
    Moderate, because profile maturity is sufficient but spread evidence is unavailable.
```

Confidence inputs:

- Profile maturity.
- Agreement between price, volume, VWAP, Volume Profile, and Market Profile.
- Number of confirming structures.
- Quality of prior state detection.
- Presence or absence of news/event distortion.
- Session context: RTH, ETH, prior day, composite.

Suggested confidence formula:

```text
transition_confidence =
    0.30 * current_state_confidence
  + 0.25 * evidence_alignment
  + 0.20 * profile_maturity
  + 0.15 * structure_quality
  + 0.10 * session_context_quality
```

## 1. Consensus

### Definition

Consensus is a state where participants appear to broadly agree on value.

### Common Predecessor States

- Fear Pressure resolving into balance.
- Conviction maturing into accepted value.
- Value Migration stabilizing.
- Failed Auction returning to prior value.
- Liquidation ending in excess.

### Common Successor States

- Belief Acceleration.
- Rotation.
- Value Migration.
- Crowd Fragility.
- Failed Auction.

### Typical Profile Structures Associated With Transition

- Balanced profile.
- Mature value area.
- Overlapping value.
- Poor high or poor low at balance edge.
- Initial balance containment.
- Compression around POC.

### Typical Volume Profile Evidence

- High volume near POC.
- Large share of volume inside value area.
- Stable high-volume node.
- Low-volume nodes marking balance edges.

### Typical Market Profile Evidence

- High TPO count near value.
- Rotational structure.
- Few single prints.
- Mature initial balance.
- Balanced day type.

### Typical VWAP Evidence

- Price repeatedly returns to VWAP.
- VWAP slope is flat or mild.
- Balanced time above and below VWAP.

### Confidence Factors

Increase confidence when:

- Time and volume both cluster near value.
- VWAP is repeatedly revisited.
- Profile is mature.

Decrease confidence when:

- Balance is immature.
- Volume is thin.
- Profile has unresolved poor extremes.

### Failure Modes

- Mistaking low volatility for true consensus.
- Ignoring event risk.
- Treating overnight balance as equivalent to RTH consensus.

## 2. Belief Acceleration

### Definition

Belief Acceleration is the state where collective belief appears to be changing faster than before.

### Common Predecessor States

- Consensus.
- Regret Potential.
- Failed Auction.
- Value Migration.

### Common Successor States

- Conviction.
- FOMO Pressure.
- Fear Pressure.
- Failed Auction.
- Trapped Participation.

### Typical Profile Structures Associated With Transition

- Break from balance.
- Initial balance breakout.
- Single prints.
- Low-volume node traversal.
- Double distribution beginning to form.
- Poor high/low repair.

### Typical Volume Profile Evidence

- Volume expands away from prior value.
- Price moves quickly through low-volume zones.
- New volume begins building outside prior value.

### Typical Market Profile Evidence

- Single prints.
- Directional TPO expansion.
- Failed return to prior balance.
- New distribution forming.

### Typical VWAP Evidence

- Price separates from VWAP.
- VWAP slope begins changing.
- Pullbacks fail to return fully to VWAP.

### Confidence Factors

Increase confidence when:

- Price velocity, volume, and VWAP slope align.
- Profile shows clean directional expansion.
- Prior balance was mature.

Decrease confidence when:

- Move occurs on low volume.
- Price quickly returns into value.
- VWAP does not respond.

### Failure Modes

- Mistaking one-bar volatility for belief change.
- Ignoring news shocks.
- Overweighting price without volume or profile confirmation.

## 3. Conviction

### Definition

Conviction is persistent directional participation supported by price, time, volume, and value acceptance.

### Common Predecessor States

- Belief Acceleration.
- Value Migration.
- Regret Potential.
- FOMO Pressure that becomes accepted.

### Common Successor States

- Value Migration.
- New Consensus.
- FOMO Pressure.
- Crowd Fragility.
- Exhaustion.

### Typical Profile Structures Associated With Transition

- Trend day.
- Accepted initial balance breakout.
- Double distribution with second distribution holding.
- POC migration.
- Value area migration.
- Single prints that remain unrepaired.

### Typical Volume Profile Evidence

- Volume builds in direction of movement.
- POC shifts directionally.
- New high-volume node forms away from prior value.
- Pullbacks hold above/below accepted nodes.

### Typical Market Profile Evidence

- Directional TPO development.
- Higher/lower value.
- Single prints supporting movement.
- Few successful returns to prior value.

### Typical VWAP Evidence

- Price holds mostly above/below VWAP.
- VWAP slope aligns with direction.
- Pullbacks to VWAP are absorbed.

### Confidence Factors

Increase confidence when:

- VWAP, POC, and value area migrate together.
- Pullbacks are shallow and absorbed.
- Volume confirms direction.

Decrease confidence when:

- Price moves without value migration.
- Volume fades.
- POC remains anchored to prior value.

### Failure Modes

- Confusing short covering or long liquidation with durable conviction.
- Mistaking low-volume drift for conviction.
- Ignoring nearby higher timeframe value.

## 4. FOMO Pressure

### Definition

FOMO Pressure is urgent participation after price has already moved.

### Common Predecessor States

- Belief Acceleration.
- Conviction.
- Regret Potential.
- Breakout from Consensus.

### Common Successor States

- Conviction.
- Value Migration.
- Crowd Fragility.
- Trapped Participation.
- Failed Auction.

### Typical Profile Structures Associated With Transition

- Extension beyond value.
- Single prints.
- Poor high in upside chase.
- Poor low in downside chase.
- P-shaped profile.
- Initial balance breakout.

### Typical Volume Profile Evidence

- Late volume expansion.
- Volume builds above/below prior value.
- Low-volume nodes are crossed quickly.
- Volume concentration near new extremes.

### Typical Market Profile Evidence

- Fast TPO expansion.
- Single prints.
- Thin auction zones.
- New distribution starting away from prior value.

### Typical VWAP Evidence

- Price extended from VWAP.
- VWAP slope follows but lags.
- Pullbacks do not fully test VWAP.

### Confidence Factors

Increase confidence when:

- Extension and volume expansion agree.
- Price accepts outside prior value.
- Single prints remain unrepaired.

Decrease confidence when:

- Volume does not confirm.
- Price returns quickly to VWAP.
- Breakout fails to hold outside value.

### Failure Modes

- Mistaking legitimate repricing for FOMO.
- Treating all extension as emotional.
- Ignoring product-specific volatility.

## 5. Fear Pressure

### Definition

Fear Pressure is urgent selling, hedging, liquidation, or risk avoidance.

### Common Predecessor States

- Crowd Fragility.
- Trapped Participation.
- Failed Auction.
- Belief Acceleration downward.
- Broken Consensus.

### Common Successor States

- Liquidation.
- Excess Low.
- New Consensus.
- Regret Potential.
- Trapped Participation.

### Typical Profile Structures Associated With Transition

- b-shaped profile.
- Downside single prints.
- Failed upside auction.
- Break below value.
- Poor low pressing lower.
- Excess low after liquidation.

### Typical Volume Profile Evidence

- Volume expands on downside.
- High-volume failure zone above market.
- Thin volume below value.
- New lower volume node forms after liquidation.

### Typical Market Profile Evidence

- Downside TPO expansion.
- Single prints lower.
- Failed returns to value.
- Excess low if selling completes.

### Typical VWAP Evidence

- VWAP loss.
- Failed VWAP reclaim.
- Price remains below VWAP.
- VWAP slope turns lower.

### Confidence Factors

Increase confidence when:

- Downside velocity and volume expand together.
- VWAP reclaim fails.
- Price accepts below value.

Decrease confidence when:

- Downside move quickly reclaims VWAP.
- Selling occurs on low volume.
- Strong excess low forms and holds.

### Failure Modes

- Confusing normal pullback with fear.
- Overreacting to one liquidation bar.
- Missing absorption by responsive buyers.

## 6. Crowd Fragility

### Definition

Crowd Fragility is the market's susceptibility to rapid repositioning if the crowd is forced to change behavior.

### Common Predecessor States

- FOMO Pressure.
- Conviction.
- Consensus near a vulnerable edge.
- Value Migration that lacks acceptance.
- Trapped Participation.

### Common Successor States

- Fear Pressure.
- Trapped Participation.
- Failed Auction.
- Reversal.
- Renewed Conviction.

### Typical Profile Structures Associated With Transition

- Failed auction.
- Poor high/low after extension.
- High-volume extreme.
- Thin single-print area nearby.
- Double distribution failure.
- Unfinished auction.

### Typical Volume Profile Evidence

- High volume near vulnerable extreme.
- Low-volume area between price and prior value.
- Volume concentration outside value.
- Weak POC migration.

### Typical Market Profile Evidence

- Thin structure below longs or above shorts.
- Single prints vulnerable to repair.
- Failed acceptance.
- Poor extreme.

### Typical VWAP Evidence

- Price far from VWAP.
- VWAP lagging price.
- Price begins rotating back toward VWAP.

### Confidence Factors

Increase confidence when:

- Heavy participation occurs at failed extreme.
- Thin structure lies nearby.
- VWAP is distant and price starts reverting.

Decrease confidence when:

- Value migrates cleanly.
- Pullbacks are absorbed.
- POC supports the new area.

### Failure Modes

- Calling every extension fragile.
- Ignoring valid trend structure.
- Missing genuine value migration.

## 7. Regret Potential

### Definition

Regret Potential is the chance that sidelined or wrong-footed participants will be forced to chase, exit, or reverse.

### Common Predecessor States

- Consensus.
- Failed Auction.
- Trapped Participation.
- Belief Acceleration.
- Conviction.

### Common Successor States

- FOMO Pressure.
- Fear Pressure.
- Conviction.
- Value Migration.
- Trapped Participation.

### Typical Profile Structures Associated With Transition

- Break from mature balance.
- Failed pullback to prior value.
- Poor high/low repair.
- Single prints.
- Double distribution transition.

### Typical Volume Profile Evidence

- Prior high-volume node abandoned.
- New volume builds away from old value.
- Thin area prevents easy re-entry.
- Volume appears late after movement.

### Typical Market Profile Evidence

- Fast movement from balance.
- Little time offered for re-entry.
- Single prints remain unrepaired.
- Old value rejects retest.

### Typical VWAP Evidence

- Price separates from VWAP.
- VWAP catches up slowly.
- Pullback to VWAP fails or is shallow.

### Confidence Factors

Increase confidence when:

- Prior balance was mature.
- Breakout offers little retest.
- Participants are visibly trapped or left behind.

Decrease confidence when:

- Price returns easily to prior value.
- Move lacks volume.
- Profile remains rotational.

### Failure Modes

- Inferring regret where no clear participation existed.
- Treating every missed move as regret-producing.
- Ignoring higher timeframe context.

## 8. Value Migration

### Definition

Value Migration is the movement of accepted value from one area to another.

### Common Predecessor States

- Belief Acceleration.
- Conviction.
- FOMO Pressure that becomes accepted.
- Fear Pressure that resolves lower.
- Regret Potential.

### Common Successor States

- New Consensus.
- Conviction.
- FOMO Pressure.
- Crowd Fragility if migration fails.
- Trapped Participation if migration reverses.

### Typical Profile Structures Associated With Transition

- POC migration.
- Value area migration.
- Double distribution.
- Accepted initial balance breakout.
- Old value rejection.

### Typical Volume Profile Evidence

- POC shifts.
- Volume builds in new area.
- Prior POC loses attraction.
- New high-volume node forms.

### Typical Market Profile Evidence

- Time builds in new distribution.
- Old value retests fail.
- New value area separates from prior value.

### Typical VWAP Evidence

- VWAP slope aligns with migration.
- Price spends more time on one side of VWAP.
- VWAP pullbacks support the new value.

### Confidence Factors

Increase confidence when:

- Time and volume both build in the new area.
- POC and value area migrate together.
- Old value is rejected.

Decrease confidence when:

- Price moves but volume does not follow.
- POC remains at old value.
- Profile is immature.

### Failure Modes

- Mistaking price movement for value movement.
- Overweighting early-session profile shifts.
- Missing composite profile resistance/support.

## 9. Trapped Participation

### Definition

Trapped Participation is a state where participants are positioned at prices that become structurally unfavorable.

### Common Predecessor States

- Failed Auction.
- FOMO Pressure.
- Crowd Fragility.
- Failed Value Migration.
- Poor high/low repair failure.

### Common Successor States

- Fear Pressure.
- Regret Potential.
- Liquidation.
- Reversal.
- New Consensus after absorption.

### Typical Profile Structures Associated With Transition

- Failed auction.
- Excess high after upside failure.
- Excess low after downside failure.
- Failed initial balance breakout.
- Double distribution failure.
- High-volume failed extreme.

### Typical Volume Profile Evidence

- High volume at failed level.
- Price returns through high-participation zone.
- Volume concentration outside value.
- New value fails to hold.

### Typical Market Profile Evidence

- Failed acceptance outside value.
- Return through single prints.
- Poor extreme followed by reversal.
- Old value reclaimed.

### Typical VWAP Evidence

- VWAP reclaim after downside trap.
- VWAP loss after upside trap.
- Price crosses VWAP against trapped participants.

### Confidence Factors

Increase confidence when:

- Failure follows high participation.
- Price quickly returns through the entry area.
- VWAP confirms reversal.

Decrease confidence when:

- Participation was low.
- Price consolidates constructively.
- New value still forms outside prior value.

### Failure Modes

- Assuming every failed move traps meaningful size.
- Ignoring absorption.
- Misreading high volume as wrong-sided participation.

## Common Transition Examples

### Consensus To Belief Acceleration

```text
Mature balance
  -> price breaks value edge
  -> volume expands
  -> single prints form
  -> VWAP slope turns
```

Historical examples:

- Index futures balancing before a central bank release, then repricing sharply.
- Crude oil balancing before inventory data, then breaking through low-volume structure.

### Belief Acceleration To Conviction

```text
Fast movement
  -> pullbacks are shallow
  -> POC migrates
  -> value area follows
  -> VWAP supports direction
```

Historical examples:

- Trend day after a mature multi-day balance.
- Commodity repricing with volume building in the new area.

### FOMO Pressure To Crowd Fragility

```text
Extended price
  -> late volume surge
  -> poor high/low
  -> price stalls outside value
  -> thin structure lies behind move
```

Historical examples:

- Failed upside breakout after late buyers chase above prior value.
- Short-covering rally that stalls at a high-volume extreme.

### Crowd Fragility To Fear Pressure

```text
Vulnerable positioning
  -> failed acceptance
  -> VWAP loss/reclaim against crowd
  -> price returns through thin structure
  -> liquidation begins
```

Historical examples:

- Equity index liquidation after failed breakout.
- Commodity reversal after spike above value fails.

### Fear Pressure To New Consensus

```text
Liquidation
  -> excess low forms
  -> volume builds lower
  -> VWAP flattens
  -> new value area forms
```

Historical examples:

- Risk-off selloff stabilizing into afternoon balance.
- Long liquidation in futures followed by lower accepted value.

## Uncommon Transition Examples

### Consensus Directly To Fear Pressure

Possible during:

- News shock.
- Geopolitical event.
- Surprise economic release.
- Sudden liquidity withdrawal.

Evidence:

- Price gaps away from value.
- VWAP immediately loses relevance.
- Volume expands violently.

### FOMO Pressure To New Consensus

Possible when:

- Chase behavior is absorbed.
- New higher/lower value forms quickly.
- Late participation becomes accepted instead of trapped.

Evidence:

- New POC forms.
- Value area migrates.
- Pullbacks hold.

### Crowd Fragility To Renewed Conviction

Possible when:

- A vulnerable-looking pullback is absorbed.
- Price re-accepts outside value.
- VWAP supports the move.

Evidence:

- Failed reversal.
- New value forms.
- Prior fragile zone becomes support/resistance.

## Transition Forecast Output

Design-only structure:

```python
BehavioralTransitionForecast:
    current_state: str
    current_state_confidence: float
    likely_transitions: list[TransitionEstimate]
    narrative: str
    evidence: list[str]
    warnings: list[str]

TransitionEstimate:
    next_state: str
    probability_band: str
    confidence: float
    supporting_evidence: list[str]
    failure_modes: list[str]
```

Narrative example:

```text
The market currently shows mature Consensus with rising Belief Acceleration risk.
Price is pressing the upper edge of value, volume is beginning to expand, and the
initial balance high is under pressure. The probability of continuation into
Value Migration is elevated if price accepts above value. However, a failed
auction back into value would increase the probability of rotation and trapped
participation. This is a behavioral transition forecast, not a trade
recommendation.
```

## Non-Goals

- No direct trade calls.
- No entries, stops, or targets.
- No automated execution.
- No claim of prediction certainty.
- No replacement for human judgment.
- No portfolio sizing.
