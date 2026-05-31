# Agent Framework Design

## 1. Objective

Design a lightweight agent framework that supports domain-specific behavior while preserving the existing assistant guarantees:

- Local-first model routing.
- Domain-aware memory retrieval.
- Memory type filtering.
- Centralized escalation control.
- Simple rule-based domain detection for now.

The framework should introduce domain agents as prompt and behavior specialists, not as independent model callers or memory owners.

## 2. Proposed Folder Structure

```text
app/
  agents/
    __init__.py
    base.py
    registry.py
    trading.py
    medical.py
    build.py

  llm/
    service.py
    router.py
    client.py

  memory/
    store.py
    logger.py

  prompts/
    __init__.py
    builder.py
```

Responsibilities:

- `app/agents/base.py`: shared agent interface.
- `app/agents/registry.py`: agent registration and lookup.
- `app/agents/trading.py`: `TradingAgent`.
- `app/agents/medical.py`: `MedicalAgent`.
- `app/agents/build.py`: `BuildAgent`.
- `app/prompts/builder.py`: optional shared prompt assembly helpers once prompt-building grows.
- `app/llm/service.py`: orchestration, memory retrieval, model calls, escalation, memory writes.

## 3. Agent Interface Design

Agents should shape domain-specific behavior without owning infrastructure.

Conceptual interface:

```python
class Agent:
    domain: str

    def should_handle(self, prompt: str) -> bool:
        ...

    def build_prompt(
        self,
        user_prompt: str,
        authoritative_memory: list[str],
        reference_memory: list[str],
        background_memory: list[str],
    ) -> str:
        ...

    def preferred_task_type(self, prompt: str) -> str | None:
        ...

    def classify_memory_type(self, prompt: str, answer: str) -> str | None:
        ...
```

Agent responsibilities:

- Provide domain-specific prompt framing.
- Optionally hint whether a task should use fast or reasoning local models.
- Optionally provide domain-specific memory classification hints.
- Keep domain language, safety framing, and response shape consistent.

Agents should not:

- Call Ollama directly.
- Call OpenAI directly.
- Write to memory directly.
- Query Chroma directly.
- Decide remote escalation directly.

## 4. Agent Registration Mechanism

Use an explicit registry rather than dynamic imports at first.

Conceptual registry:

```python
class AgentRegistry:
    def register(self, agent: Agent) -> None:
        ...

    def get(self, domain: str) -> Agent:
        ...

    def resolve(self, prompt: str, domain: str) -> Agent:
        ...
```

Initial registration:

```text
trading  -> TradingAgent
medicine -> MedicalAgent
build    -> BuildAgent
general  -> DefaultAgent or no-op fallback
```

The registry should be constructed once during service initialization.

## 5. Domain Routing Flow

Domain detection remains deterministic and cheap.

```text
User prompt
  -> LLMService._detect_domain(prompt)
  -> domain: trading | medicine | build | general
  -> AgentRegistry.get(domain)
  -> selected agent
```

Examples:

```text
"What is VWAP and how is it used with volume profile?"
  -> domain=trading
  -> TradingAgent

"What are red flags for chest pain?"
  -> domain=medicine
  -> MedicalAgent

"How should I structure the agent framework for this local AI assistant?"
  -> domain=build
  -> BuildAgent
```

Future versions can add subdomain routing after the first domain match.

## 6. Memory Interaction Flow

Memory retrieval should remain centralized in `LLMService` or a dedicated memory orchestration helper.

Retrieval priority:

```text
1. authoritative same-domain memories
2. reference same-domain memories
3. optional cross-domain reference memories
```

Ephemeral memories are not retrieved because they should not be stored by default.

Flow:

```text
LLMService
  -> detect domain
  -> retrieve authoritative same-domain memory
  -> retrieve reference same-domain memory
  -> retrieve optional cross-domain reference memory
  -> pass grouped memory to selected agent
  -> agent builds prompt
```

Agents receive memory groups as inputs but do not query storage directly.

## 7. Model Selection Flow

Model selection remains local-first and centrally controlled.

```text
User prompt
  -> domain detection
  -> agent selection
  -> memory retrieval
  -> prompt building
  -> router.classify(prompt)
  -> local model:
       - mistral for simple
       - qwen3:14b for complex
  -> escalation check
  -> remote fallback only if weak/non-answer
```

Agents may provide a task-type hint, but the service should treat it as advisory.

Example:

```text
BuildAgent.preferred_task_type(prompt)
  -> reasoning
```

This should choose the stronger local model, not bypass local-first behavior.

## 8. Initial Agents

### TradingAgent

Purpose:

- Trading concepts.
- Market structure.
- VWAP, volume profile, order flow, support/resistance, futures, risk rules.

Prompt framing:

```text
Authoritative trading rules:
...

Reference trading context:
...

Optional background:
...

User request:
...
```

Memory classification hints:

- Durable trading rules -> `authoritative`.
- Reusable trading explanations -> `reference`.
- One-off market commentary -> `ephemeral`.

### MedicalAgent

Purpose:

- Medical explanations.
- Symptoms.
- Treatment concepts.
- Durable medical heuristics.

Prompt framing should include safety language:

```text
Use medical memory as heuristic context, not diagnosis.
Escalate uncertainty and red flags clearly.

Authoritative medical heuristics:
...

Reference medical context:
...

User request:
...
```

Memory classification hints:

- Durable clinical heuristics -> `authoritative`.
- Reusable medical explanations -> `reference`.
- One-off symptom Q&A -> `ephemeral`.

### BuildAgent

Purpose:

- Architecture.
- Implementation planning.
- Agent framework design.
- Memory systems.
- Routing, prompt builders, vector databases, local models, service layers.

Prompt framing:

```text
Durable build decisions:
...

Reference build context:
...

Optional background:
...

User request:
...
```

Memory classification hints:

- Architecture decisions -> `authoritative`.
- Reusable implementation explanations -> `reference`.
- Temporary debugging output -> `ephemeral`.

## 9. Future Agents

### SpreadMatrixAgent

Likely parent domain:

```text
trading
```

Purpose:

- Futures spread matrix analysis.
- Calendar spread logic.
- Relative value.
- Contract relationships.
- Seasonality.

Possible routing:

```text
domain=trading
subdomain=spread_matrix
agent=SpreadMatrixAgent
```

### PortfolioAgent

Likely parent domain:

```text
trading
```

Future possible domain:

```text
finance
```

Purpose:

- Allocation.
- Risk exposure.
- Position sizing.
- Drawdown analysis.
- Portfolio-level rules.

Possible routing:

```text
domain=trading
subdomain=portfolio
agent=PortfolioAgent
```

### FunctionalMedicineAgent

Parent domain:

```text
medicine
```

Purpose:

- Functional medicine heuristics.
- Lab interpretation context.
- Supplement and lifestyle frameworks.
- Root-cause models.

Safety posture:

- Preserve medical uncertainty.
- Clearly distinguish educational support from diagnosis.
- Emphasize clinician review for red flags or treatment changes.

## 10. Text Architecture Diagrams

Overall flow:

```text
User Prompt
    |
    v
Domain Detection
    |
    v
Agent Registry
    |
    v
Selected Agent
    |
    v
Memory Retrieval
    |
    +--> authoritative same-domain
    +--> reference same-domain
    +--> optional cross-domain reference
    |
    v
Agent Prompt Builder
    |
    v
Local-First Model Router
    |
    +--> mistral
    +--> qwen3:14b
    |
    v
Local Model Response
    |
    v
Escalation Check
    |
    +--> keep local response
    +--> remote fallback only if weak/non-answer
    |
    v
Memory Type Classification
    |
    +--> authoritative: store
    +--> reference: store
    +--> ephemeral: skip
    |
    v
Final Response
```

Agent boundary:

```text
+--------------------+
|     LLMService     |
|--------------------|
| domain detection   |
| registry lookup    |
| memory retrieval   |
| model execution    |
| escalation checks  |
| memory writes      |
+---------+----------+
          |
          v
+--------------------+
|       Agent        |
|--------------------|
| domain prompt form |
| domain heuristics  |
| optional task hint |
| memory type hints  |
+--------------------+
```

Memory priority:

```text
Prompt domain = build

1. Search:
   domain=build, memory_type=authoritative

2. Search:
   domain=build, memory_type=reference

3. Optional:
   memory_type=reference, domain != build

4. Exclude:
   memory_type=ephemeral
```

Future sub-agent routing:

```text
User Prompt
    |
    v
Domain Detection
    |
    v
Subdomain Detection
    |
    +--> trading/spread_matrix -> SpreadMatrixAgent
    +--> trading/portfolio     -> PortfolioAgent
    +--> medicine/functional   -> FunctionalMedicineAgent
    |
    v
Fallback Domain Agent
```

## 11. Advantages

- Keeps model execution centralized and local-first.
- Makes domain behavior explicit and testable.
- Prevents agents from becoming hidden model clients.
- Preserves existing memory metadata and retrieval strategy.
- Allows incremental rollout: start with prompt building, then add hints.
- Supports future specialized agents without rewriting `LLMService`.
- Makes medical and trading safety/precision framing easier to maintain.

## 12. Risks

- Too much logic in agents could fragment behavior if boundaries are not enforced.
- Rule-based domain detection may misclassify prompts until keywords improve.
- Agent-specific memory classification can conflict with central memory filtering unless clearly ordered.
- Cross-domain memory can pollute prompts if optional background is too broad.
- Sub-agent routing could become brittle without tests.
- Medical agents need careful language to avoid unsafe certainty.

## 13. Recommended Implementation Order

1. Add `app/agents/base.py` with the agent interface.
2. Add `DefaultAgent` or fallback behavior.
3. Add `TradingAgent`, `MedicalAgent`, and `BuildAgent`.
4. Add `AgentRegistry` with explicit registration.
5. Update `LLMService` to resolve an agent after domain detection.
6. Move prompt-building responsibility into agents.
7. Keep memory retrieval, model calls, escalation, and memory writes in `LLMService`.
8. Add lightweight tests for domain-to-agent resolution.
9. Add tests for agent prompt building with memory groups.
10. Add optional agent task-type hints.
11. Add optional agent memory-type hints.
12. Add subdomain routing for future agents.
13. Implement `SpreadMatrixAgent`, `PortfolioAgent`, and `FunctionalMedicineAgent` after the base pattern is stable.
