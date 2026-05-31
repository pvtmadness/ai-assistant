# TradingAgent Behavioral Market Research Design

## 1. Objective

Design the research scaffold for evolving `TradingAgent` into a behavioral market structure agent.

The goal is not to predict price mechanically from indicators. The goal is to model what observable market structures may reveal about deeper crowd behavior: collective belief, FOMO, fear, conviction, consensus, fragility, regret, trapped participation, and likely state transitions.

This document is design-only. It proposes concepts, variables, proxies, data structures, experiments, and a roadmap for later implementation.

## 2. Core Hypothesis

Markets are behavioral systems.

Price is not the market itself. Price is a visible trace left by participants acting under uncertainty, incentive, fear, leverage, urgency, regret, and social feedback.

Price, time, and volume can be treated as behavioral evidence:

- Price shows where participants were willing or forced to transact.
- Time shows where acceptance, hesitation, or neglect occurred.
- Volume shows where participation concentrated or vanished.
- VWAP shows a dynamic benchmark of average participation.
- Market Profile may reveal time-based acceptance and rejection.
- Volume Profile may reveal crowd commitment, liquidity memory, and trapped participation.
- Spread relationships may reveal relative belief, stress, substitution, and institutional positioning.

Core hypothesis:

```text
Market Profile and Volume Profile may encode crowd state.
```

They may help infer whether a market is balanced, emotionally extended, fragile, repricing, distributing, accumulating, or transitioning between states.

## 3. Proposed Behavioral State Variables

### Consensus

Degree to which participants appear to agree on value.

High consensus may appear as:

- Extended time spent near value.
- High volume at accepted prices.
- Narrow range development.
- Repeated reversion to value.

Low consensus may appear as:

- Fast directional movement.
- Poor structure.
- Thin volume zones.
- Rejection from prior value.

### FOMO Pressure

Urgency to participate after price has moved.

Possible signs:

- Price accelerating away from value.
- Late volume expansion.
- Chasing behavior above/below VWAP.
- Breakout through low-volume areas.
- Reduced pullback depth.

### Fear Pressure

Urgency to exit, hedge, liquidate, or avoid risk.

Possible signs:

- Sharp price movement with expanding volume.
- Fast rejection of prior value.
- Gaps or thin auction areas.
- VWAP loss with poor recovery.
- Failed acceptance above important value areas.

### Conviction

Persistence and quality of participation in one direction.

Possible signs:

- Price holding above/below VWAP.
- Value migration in the direction of trade.
- Pullbacks absorbed quickly.
- Volume confirming directional movement.
- Market Profile building higher/lower accepted value.

### Crowd Fragility

Susceptibility of the crowd to rapid repositioning.

Possible signs:

- Large participation concentrated at vulnerable levels.
- Price far from accepted value.
- Thin volume below longs or above shorts.
- Failed breakout after heavy participation.
- Spread divergence or confirmation breakdown.

### Regret Potential

Potential for participants to feel forced to re-enter, exit, or chase after missing or misjudging a move.

Possible signs:

- Failed tests of prior value.
- Rapid return through low-volume areas.
- Breakout retest that holds.
- Strong movement after long balance.
- Late participants trapped away from value.

### Belief Acceleration

Rate at which market belief appears to be changing.

Possible signs:

- Increasing price velocity.
- Volume expansion away from value.
- VWAP slope change.
- Rapid value migration.
- Spread relationships confirming repricing.

### Value Migration

Movement of accepted value over time.

Possible signs:

- Point of Control shifting higher/lower.
- Value Area migrating.
- Market Profile distribution building in a new zone.
- VWAP slope aligning with new value.
- Prior high-volume nodes becoming support/resistance.

### Trapped Participation

Participants positioned at prices that become unfavorable and may later become fuel for movement.

Possible signs:

- High volume near failed breakout/breakdown levels.
- Price returning through prior high-participation zones.
- Failed acceptance outside value.
- VWAP reclaim/loss after heavy participation.
- Spread relationship reversal after crowded positioning.

## 4. Possible Measurable Proxies

### Price

Potential proxies:

- Distance from session VWAP.
- Distance from prior value area.
- Range extension beyond balance.
- Failed breakout or breakdown.
- Rate of change.
- Rotation size.
- Acceptance above/below key levels.

Behavioral interpretation:

- Distance from value may indicate emotional extension.
- Failed movement may reveal trapped participation.
- Acceptance may indicate consensus migration.

### Time

Potential proxies:

- Time spent at price.
- Time above/below VWAP.
- Time outside prior value.
- Duration of balance.
- Speed of return into value.

Behavioral interpretation:

- Time creates acceptance.
- Rejection with little time may indicate poor consensus.
- Long balance may store future energy or disagreement.

### Volume

Potential proxies:

- Volume at price.
- Volume expansion on directional movement.
- Volume divergence from price movement.
- Relative volume versus recent baseline.
- Volume concentration after breakout.

Behavioral interpretation:

- Volume shows participation intensity.
- Late volume can indicate chase or liquidation.
- High volume followed by failure may indicate trapped participants.

### VWAP

Potential proxies:

- Price distance from VWAP.
- VWAP slope.
- VWAP reclaim/loss.
- Time spent above/below VWAP.
- Pullback response at VWAP.

Behavioral interpretation:

- VWAP can serve as a live crowd cost basis.
- Reclaim/loss may signal change in control.
- Persistent distance from VWAP may imply conviction or emotional extension.

### Volume Profile

Potential proxies:

- Point of Control location.
- Value Area High/Low.
- High Volume Nodes.
- Low Volume Nodes.
- Volume shelves.
- Volume gaps.
- Profile shape.

Behavioral interpretation:

- High-volume areas may represent accepted belief.
- Low-volume areas may represent rejection or fragile auction zones.
- Failed acceptance beyond value can reveal trapped participation.

### Market Profile

Potential proxies:

- Time Price Opportunity count.
- Initial balance behavior.
- Single prints.
- Balanced vs trend day structure.
- Value migration by session.
- Poor highs/lows.

Behavioral interpretation:

- Time at price may represent acceptance.
- Single prints may indicate emotional imbalance.
- Poor structure may indicate unfinished auction behavior.

### Spread Relationships

Potential proxies:

- Calendar spread widening/narrowing.
- Intermarket spread divergence.
- Relative strength against related contracts.
- Lead/lag relationships.
- Spread confirmation of outright price movement.

Behavioral interpretation:

- Spreads may reveal institutional preference.
- Divergence may indicate fragile outright movement.
- Relative repricing may reveal changing belief across time, geography, or substitute instruments.

## 5. How This Differs From Normal Technical Analysis

Normal technical analysis often asks:

```text
What pattern is on the chart?
What signal does this indicator produce?
Where is support or resistance?
```

Behavioral market structure analysis asks:

```text
What crowd state produced this structure?
Who is likely confident, trapped, late, afraid, or absent?
Where has value been accepted or rejected?
What would force participants to change behavior?
What state transition is becoming more likely?
```

The distinction:

- Indicators are treated as evidence, not signals.
- Levels are interpreted through participation and acceptance.
- Volume is interpreted as crowd commitment, not just activity.
- Failed structure matters because it reveals behavioral stress.
- The goal is state inference, not pattern matching.

## 6. Future Integration Paths

### TradingAgent

`TradingAgent` could use behavioral state analysis to:

- Explain market structure in behavioral terms.
- Distinguish trend, balance, liquidation, absorption, and failed auction states.
- Identify likely trapped participation.
- Improve explanations of VWAP, Volume Profile, and Market Profile.
- Generate structured hypotheses rather than direct trade calls.

### SpreadMatrixAgent

`SpreadMatrixAgent` could use the scaffold to:

- Interpret spread movement as changing collective belief across contracts.
- Detect relative crowding or stress.
- Compare outright price behavior against spread confirmation.
- Model belief migration across expirations or related markets.

### PortfolioAgent

`PortfolioAgent` could use behavioral state analysis to:

- Estimate crowd fragility across positions.
- Identify correlated behavioral risk.
- Detect crowded exposure.
- Adjust risk framing when multiple markets show similar fear/FOMO states.
- Translate market state into portfolio-level caution or opportunity.

## 7. Proposed Data Structures

Design only. Names are provisional.

### MarketObservation

```python
MarketObservation:
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    vwap: float | None
    session_high: float | None
    session_low: float | None
    prior_close: float | None
```

### ProfileSnapshot

```python
ProfileSnapshot:
    symbol: str
    session: str
    point_of_control: float
    value_area_high: float
    value_area_low: float
    high_volume_nodes: list[float]
    low_volume_nodes: list[float]
    profile_shape: str
```

### MarketProfileSnapshot

```python
MarketProfileSnapshot:
    symbol: str
    session: str
    initial_balance_high: float
    initial_balance_low: float
    time_at_price: dict[float, int]
    single_prints: list[float]
    day_type: str | None
```

### SpreadObservation

```python
SpreadObservation:
    spread_name: str
    leg_a: str
    leg_b: str
    spread_value: float
    spread_change: float
    relative_strength: float | None
```

### BehavioralState

```python
BehavioralState:
    consensus: float
    fomo_pressure: float
    fear_pressure: float
    conviction: float
    crowd_fragility: float
    regret_potential: float
    belief_acceleration: float
    value_migration: float
    trapped_participation: float
    confidence: float
    notes: list[str]
```

### BehavioralStateTransition

```python
BehavioralStateTransition:
    from_state: str
    to_state: str
    likelihood: float
    evidence: list[str]
```

## 8. Proposed First Experimental Module: BehavioralStateAnalyzer

Purpose:

Convert market structure observations into tentative behavioral state scores.

Design:

```text
BehavioralStateAnalyzer
  input:
    - MarketObservation series
    - ProfileSnapshot
    - MarketProfileSnapshot
    - optional SpreadObservation series

  output:
    - BehavioralState
    - evidence notes
    - possible state transitions
```

Initial responsibilities:

- Estimate consensus from time and volume acceptance.
- Estimate FOMO pressure from price extension, speed, and late volume.
- Estimate fear pressure from downside speed, rejection, and volume expansion.
- Estimate conviction from VWAP alignment and value migration.
- Estimate fragility from thin structure and trapped volume.
- Generate natural-language evidence summaries for `TradingAgent`.

Non-goals:

- No autonomous trade decisions.
- No direct order generation.
- No claim of prediction certainty.
- No portfolio sizing yet.

## 9. Research Questions To Explore Later

Books and theory areas:

- Auction Market Theory.
- Market Profile.
- Volume Profile.
- Behavioral finance.
- Reflexivity.
- Crowd psychology.
- Market microstructure.
- Liquidity and order flow.

Research questions:

1. Which profile structures most reliably indicate acceptance versus rejection?
2. Can trapped participation be approximated from high-volume failure zones?
3. Does VWAP reclaim/loss after high participation predict state transition better than price-only levels?
4. How often do low-volume nodes behave as acceleration zones versus reversal zones?
5. Can value migration distinguish true conviction from short covering or liquidation?
6. Do spread divergences reveal fragility before outright price reversals?
7. What historical market examples show high consensus before violent repricing?
8. How should Market Profile day types map to behavioral states?
9. Can regret potential be measured by time spent away from prior accepted value?
10. Which behavioral states are stable, and which tend to transition quickly?
11. How should overnight markets and regular sessions be separated?
12. How should news shocks be distinguished from endogenous crowd transitions?

Historical example categories:

- Failed breakouts after high participation.
- Liquidation breaks through low-volume areas.
- Trend days with persistent VWAP separation.
- Balance area breakouts with value migration.
- Spread divergence before outright reversal.
- Crowded consensus before volatility expansion.

## 10. Implementation Roadmap

### Design Phase

- Define behavioral state variables.
- Define observation structures.
- Map each state variable to measurable proxies.
- Decide scoring ranges and confidence rules.
- Document what the model must not infer.

### Prototype Phase

- Implement `BehavioralStateAnalyzer`.
- Start with session-level OHLCV, VWAP, and Volume Profile.
- Add Market Profile fields once available.
- Generate human-readable evidence notes.
- Feed analyzer summaries into `TradingAgent` prompts.

### Backtest Phase

- Collect historical examples.
- Label sessions manually by behavioral state.
- Compare analyzer scores to known outcomes.
- Evaluate state transitions, not simple win/loss signals.
- Track false positives around news and low-liquidity periods.

### Integration Phase

- Add analyzer output to `TradingAgent` as reference context.
- Preserve local-first model routing.
- Store durable behavioral rules as authoritative trading memory.
- Store reusable market-structure explanations as reference memory.
- Keep one-off analyses ephemeral unless promoted.
- Later expose specialized outputs to `SpreadMatrixAgent` and `PortfolioAgent`.
