# Lenovo/Laptop Architecture

## Objective

Define the next architecture phase for this local AI assistant so Lenovo becomes the durable "brain" and Laptop remains a lightweight terminal for editing, testing, Codex work, and remote access.

The goal is to keep the large, durable context in one place while still making the assistant usable from either machine.

## Hub-And-Terminal Architecture

```text
Laptop
  - lightweight terminal
  - code editing
  - Git sync
  - Codex repo-aware edits
  - small local models if available
  - OpenAI fallback if configured
  - minimal or disabled memory writes
  - future remote requests to Lenovo

        |
        | SSH / local network API / Tailscale
        v

Lenovo
  - primary brain
  - durable Chroma memory
  - project context
  - books, manuscripts, articles
  - trading and medical reference documents
  - Sierra/TradingView exports
  - stronger local Ollama models
  - main retrieval and reasoning host
```

Lenovo should hold the durable memory and large research context. Laptop should stay light, portable, and easy to keep in sync through Git without copying large memory stores or market/reference data.

## Authoritative Data Ownership

Lenovo is the authoritative source of durable data.

Durable data includes:

- Chroma memory
- Sierra Chart exports
- TradingView exports
- books
- articles
- manuscripts
- medical/reference documents
- project documents
- long-term research materials

Laptop may access these resources remotely, but Laptop should not become a second source of record.

If the same data exists on both machines, Lenovo is authoritative.

GitHub remains authoritative for code and committed documentation only. GitHub is not the storage layer for Chroma, market data, books, manuscripts, medical/reference materials, or other large private datasets.

## Lenovo Role

Lenovo is the primary development and research machine for this repo.

Responsibilities:

- Run the main local assistant loop from `app/main.py`.
- Host durable Chroma memory under `data/vector`.
- Keep long-term project context, including `docs/PROJECT_BRIEF.md`.
- Hold books, manuscripts, articles, trading data, medical/reference documents, Sierra exports, and TradingView prototype CSVs.
- Run local Ollama models for local-first behavior.
- Use Mistral for simple prompts through the current router.
- Use Qwen3:14B for complex/build prompts through the current router.
- Use OpenAI fallback only when configured and triggered by existing fallback logic.
- Keep authoritative and reference memories centralized.
- Act as the future remote reasoning endpoint for Laptop.

Recommended Lenovo `.env` posture:

```text
DEVICE_ROLE=lenovo
EXECUTION_PROFILE=lenovo_primary
MEMORY_WRITE_POLICY=enabled
```

## Laptop Role

Laptop is the mobile development and testing terminal.

Responsibilities:

- Edit code.
- Run Git operations.
- Use Codex for repo-aware changes.
- Run small local models if available.
- Use OpenAI fallback if configured.
- Test app behavior without becoming a second durable memory source.
- Eventually forward complex, memory-heavy, or research-heavy questions to Lenovo.

Laptop should not duplicate `data/vector`, large books, Sierra exports, TradingView exports, or long-term reference corpora.

Recommended Laptop `.env` posture:

```text
DEVICE_ROLE=laptop
EXECUTION_PROFILE=laptop_light
MEMORY_WRITE_POLICY=disabled
```

`MEMORY_WRITE_POLICY=build_only` can be used later if Laptop needs to preserve project-specific build notes, but the safer default is `disabled` to avoid memory divergence.

## Memory Policies

The current Phase 1 configuration supports these memory write policies:

- `enabled`: store memories normally after existing memory type filtering.
- `disabled`: skip all memory writes.
- `build_only`: write only build-domain memories.
- `manual_review`: print memory candidates for review instead of writing them.

Recommended use:

```text
Lenovo:
  MEMORY_WRITE_POLICY=enabled

Laptop:
  MEMORY_WRITE_POLICY=disabled
```

This keeps Lenovo as the single durable memory authority. Laptop can still read local memory if present, but the intended workflow is not to copy the Chroma store to Laptop.

Future memory policy:

- Laptop sends memory-heavy questions to Lenovo.
- Lenovo performs domain-aware retrieval.
- Lenovo writes durable memories after filtering.
- Laptop either writes nothing or queues memory candidates for manual review.

## Provider/Model Policies

Current behavior should remain unchanged in Phase 1:

```text
simple route:
  Ollama / Mistral

complex or build route:
  Ollama / Qwen3:14B

fallback:
  OpenAI if configured and existing fallback conditions are met
```

Recommended future behavior:

```text
Lenovo:
  simple prompts -> local Mistral
  complex/build prompts -> local Qwen3:14B
  memory-heavy prompts -> local retrieval + local model first
  fallback -> OpenAI only when needed

Laptop:
  simple prompts -> small local model if available
  complex/build prompts -> Lenovo remote brain when reachable
  memory-heavy prompts -> Lenovo remote brain
  fallback -> OpenAI if Lenovo is unavailable and fallback is allowed
```

Provider routing has not yet been changed for Laptop. The current repository still preserves local-first routing.

## Remote Access Options

### SSH One-Shot Command

Best first remote option.

Laptop can run a command over SSH that executes the assistant on Lenovo and returns the answer.

Example shape:

```text
ssh lenovo 'cd ~/ai-assistant && venv/bin/python -m app.remote.ask "question here"'
```

Advantages:

- No server process required.
- Uses familiar SSH security.
- Easy to test.
- Keeps durable memory on Lenovo.

### Local Network API

Lenovo could later expose a local-only API for remote asks.

Possible shape:

```text
Laptop CLI -> HTTP request -> Lenovo local API -> LLMService -> response
```

This is more ergonomic than SSH after the workflow is proven, but it requires authentication, port binding decisions, and careful logging.

### Tailscale Or VPN

Recommended if Laptop needs access away from the home network.

Tailscale would let Laptop reach Lenovo through a private network identity without exposing the assistant publicly.

### Direct File Sync

Not recommended for Chroma or large research data.

Git should sync code and docs. Durable memory and large data should remain centralized on Lenovo.

## Security Considerations

- Do not expose Lenovo's assistant API directly to the public internet.
- Keep `.env` out of Git.
- Do not copy OpenAI keys or other secrets into committed files.
- Use SSH keys or Tailscale identity for remote access.
- Keep Laptop memory writes disabled unless there is a specific reason to enable them.
- Avoid copying `data/vector` to Laptop, because it can create stale or conflicting memory stores.
- Log remote requests on Lenovo once remote execution exists.
- Send the smallest useful prompt/context across the network.
- Keep Sierra exports, medical/reference documents, books, and manuscripts on Lenovo unless a specific file is needed on Laptop.

## Implementation Phases

### Phase 1: Device And Memory Policy Configuration

Status: implemented.

Added configuration support for:

```text
DEVICE_ROLE
EXECUTION_PROFILE
MEMORY_WRITE_POLICY
```

Supported execution profiles:

```text
lenovo_primary
laptop_light
```

Supported memory write policies:

```text
disabled
build_only
manual_review
enabled
```

Phase 1 intentionally does not implement remote execution, provider routing changes, or laptop-specific model routing.

### Phase 2: SSH Remote Ask Prototype

Add a small remote ask path so Laptop can send one prompt to Lenovo over SSH and receive one answer.

Recommended behavior:

- Laptop keeps `MEMORY_WRITE_POLICY=disabled`.
- Lenovo runs the actual `LLMService`.
- Lenovo performs memory retrieval.
- Lenovo performs model routing.
- Lenovo performs memory writes if allowed.
- Laptop displays the returned answer.

This phase should prove the hub-and-terminal workflow before adding a server.

### Phase 3: Lenovo Local API

Add a local-only API on Lenovo after SSH remote ask works.

Recommended constraints:

- Bind only to localhost or private network interfaces.
- Require a shared token or Tailscale-only access.
- Log requests in a local file.
- Keep memory writes centralized on Lenovo.

### Phase 4: Laptop Routing Policy

Add laptop-specific routing after the remote path exists.

Possible behavior:

- Simple prompts run locally on Laptop.
- Build, trading, medical, or memory-heavy prompts route to Lenovo.
- OpenAI is used only when Lenovo is unavailable or explicit fallback is allowed.

### Phase 5: Manual Memory Review

Expand `manual_review` into an actual queue.

Possible behavior:

- Laptop queues candidate memories.
- User reviews them.
- Approved memories are sent to Lenovo.
- Lenovo writes them into the durable memory store.

### Phase 6: Data-Aware Agents On Lenovo

Keep market and reference data on Lenovo and let agents retrieve from it.

Relevant future data sources:

- Sierra Chart exports.
- TradingView prototype CSVs.
- Profile sidecars.
- Books and articles.
- Medical/reference documents.
- Project documents.

## Current Phase 1 Status

The repo now has configuration hooks for machine role and memory write policy. This means Lenovo and Laptop can run the same codebase with different `.env` settings.

Current practical setup:

```text
Lenovo:
  DEVICE_ROLE=lenovo
  EXECUTION_PROFILE=lenovo_primary
  MEMORY_WRITE_POLICY=enabled

Laptop:
  DEVICE_ROLE=laptop
  EXECUTION_PROFILE=laptop_light
  MEMORY_WRITE_POLICY=disabled
```

Current limitations:

- Laptop does not yet forward prompts to Lenovo.
- Provider/model routing is not yet device-specific.
- Remote execution is not implemented.
- Chroma remains local to whichever machine runs the app.

## Next Recommended Phase

Implement Phase 2: SSH remote ask prototype.

First implementation step:

Create a narrow command path that accepts a single prompt, runs `LLMService.ask()` on Lenovo, prints the answer, and exits. Then add a Laptop-side wrapper or command idea that invokes it over SSH.

Target flow:

```text
Laptop command
  -> SSH to Lenovo
  -> cd ~/ai-assistant
  -> run venv/bin/python -m app.remote.ask "<prompt>"
  -> Lenovo uses local memory and local-first routing
  -> answer returns to Laptop
```

This keeps the first remote phase small, reversible, and aligned with the current repo workflow.
