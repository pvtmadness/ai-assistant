# Project Brief

## Current Project

This repo is a local Python AI assistant built around a terminal workflow.

## Runtime Shape

- `app/main.py` runs the terminal loop.
- User prompts enter through `route_request()` and then `LLMService.ask()`.
- Routing chooses a local model first.
- Simple prompts use local Mistral through Ollama.
- Complex, build, and reasoning prompts use local Qwen3:14B through Ollama.
- OpenAI fallback is available through `.env` and is used only as an escalation path.

## Agent And Routing Layer

- Domain detection selects between general, trading, medicine, and build contexts.
- `BuildAgent` handles actual AI assistant development/build questions.
- Codex is used for repo-aware edits, implementation, verification, reporting, commits, and pushes when approved.

## Memory And Logs

- The memory layer uses Chroma under `data/vector`.
- Conversation logs are written to `logs/conversations.log`.
- Current memory priorities:
  - clean unsafe or polluted memory entries
  - preserve domain-aware retrieval
  - preserve memory type filtering
  - avoid storing ephemeral answers by default

## Development Workflow

- GitHub is used to sync work between machines.
- Lenovo is the primary development machine.
- Laptop is the mobile development and testing machine.

## Current Priority

1. Clean and stabilize the memory system.
2. Improve project-aware build responses.
3. Begin market data ingestion design and prototypes.
4. Start with quick TradingView CSV testing where useful.
5. Prefer Sierra Chart/Denali exports for production research data.
6. Move toward TradingView/Sierra CSV ingestion for the behavioral market research stack.
