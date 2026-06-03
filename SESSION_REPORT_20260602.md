# Session Report 20260602

## Objective

Add a project context layer for `BuildAgent` so build-domain prompts are answered using this repository's actual project context rather than a generic AI assistant roadmap.

## Problem

The prompt:

```text
what should we do next on the AI assistant build?
```

correctly routed to `BuildAgent`, but the response leaned on retrieved generic build memories and produced broad metadata/system-roadmap advice instead of grounding itself in the current local assistant project.

## Change Summary

Added:

```text
docs/PROJECT_BRIEF.md
```

Updated:

```text
app/agents/build.py
```

`BuildAgent` now loads `docs/PROJECT_BRIEF.md` and prepends it to build-domain prompt context before retrieved memories.

## Project Brief Contents

The project brief summarizes:

- Local Python AI assistant.
- `app/main.py` terminal loop.
- Router/model selection.
- Local Ollama integration.
- Mistral for simple route.
- Qwen3:14B for complex/build route.
- OpenAI fallback through `.env`.
- Chroma memory under `data/vector`.
- Conversation logs at `logs/conversations.log`.
- GitHub workflow between Lenovo and Laptop.
- Lenovo as primary development machine.
- Laptop as mobile development/testing machine.
- Codex for repo-aware edits.
- Current priority: clean memory system, then TradingView/Sierra CSV ingestion.

## Safety Behavior

If `docs/PROJECT_BRIEF.md` is missing or unreadable, `BuildAgent` does not crash. It includes a short warning in the build context and continues with retrieved memory and the user request.

## Expected Behavior

General-domain prompts should not receive the project brief.

Build-domain prompts should receive:

```text
Project brief
then retrieved build memories
then user request
```

## Verification Plan

Run:

```text
hello
what should we do next on the AI assistant build?
explain the difference between aspirin and ibuprofen
```

Expected:

- `hello` uses `DefaultAgent`, local Mistral, no project brief.
- Build prompt uses `BuildAgent`, local Qwen3:14B, project-aware answer.
- Aspirin/ibuprofen prompt uses `DefaultAgent`, local Mistral, no project brief.
