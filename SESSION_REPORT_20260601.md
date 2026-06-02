# Session Report 20260601

## Problem Discovered

A simple prompt such as:

```text
hello
```

was being routed incorrectly:

```text
route=simple
model=mistral
domain=build
agent=BuildAgent
```

The response was a fabricated executive brief instead of a normal greeting.

The same issue risked affecting other general prompts because they were being wrapped in an executive-level prompt before domain detection.

## Investigation Steps

1. Inspected `app/agents/router.py`.
2. Found that `route_request()` always called `build_executive_prompt(user_input)`.
3. Inspected `app/llm/service.py` domain detection.
4. Confirmed `BuildAgent` was selected because the executive prompt wrapper inserted build-like language, especially the word `assistant`.
5. Initially tested removing `"assistant"` from the build keyword list.
6. Re-evaluated and determined that removing `"assistant"` was not necessary.
7. Restored `"assistant"` in `app/llm/service.py`.
8. Kept only the router fix.
9. Re-ran the requested prompts after restoring `"assistant"`.

## Root Cause

`app/agents/router.py::route_request()` always replaced raw user input with the executive brief wrapper:

```python
prompt = build_executive_prompt(user_input)
```

That meant even `hello` became a prompt containing:

```text
You are an executive-level assistant.
Provide a concise, structured executive brief.
```

`LLMService._detect_domain()` then saw wrapper language such as `assistant` and incorrectly classified the prompt as `build`, causing `BuildAgent` to activate for a normal greeting.

## Code Changes

Only `app/agents/router.py` remains changed.

The active route now preserves the original user input:

```diff
-    prompt = build_executive_prompt(user_input)
+    prompt = user_input
```

The complexity classifier was also expanded so real build/framework prompts still route to the stronger local model:

```diff
-        "system", "improve", "optimize"
+        "system", "improve", "optimize", "build",
+        "framework", "architecture"
```

No changes remain in `app/llm/service.py` for this fix.

## Test Results

### Test 1: hello

Prompt:

```text
hello
```

Flow:

```text
[Flow] prompt → router → model | route=simple model=mistral
[Flow] domain detected | domain=general
[Flow] domain → agent | agent=DefaultAgent
[Flow] simple route → memory skipped
[Flow] model(local) | provider=ollama model=mistral
[Flow] final provider=local
[Flow] model → response | response_chars=166
[Memory-Write] skipped memory_type=ephemeral domain=general
```

Result:

```text
Hello! How can I help you today? Is there a specific question or topic you'd like to discuss? I'm here to provide information and answer any questions you might have.
```

Outcome:

```text
PASS
```

### Test 2: explain the difference between aspirin and ibuprofen

Prompt:

```text
explain the difference between aspirin and ibuprofen
```

Flow:

```text
[Flow] prompt → router → model | route=simple model=mistral
[Flow] domain detected | domain=general
[Flow] domain → agent | agent=DefaultAgent
[Flow] simple route → memory skipped
[Flow] model(local) | provider=ollama model=mistral
[Flow] final provider=local
[Flow] model → response | response_chars=2735
[Memory-Write] skipped memory_type=ephemeral domain=general
```

Result:

```text
Returned a normal explanatory comparison of aspirin and ibuprofen covering mechanism, dosage/forms, blood-thinning effect, side effects, uses, and drug interactions.
```

Outcome:

```text
PASS
```

### Test 3: what should we do next on the AI assistant build?

Prompt:

```text
what should we do next on the AI assistant build?
```

Flow:

```text
[Flow] prompt → router → model | route=complex model=qwen3:14b
[Flow] domain detected | domain=build
[Flow] domain → agent | agent=BuildAgent
[Flow] router → memory/tools | domain=build authoritative_count=1 reference_count=3
[Flow] memory/tools → background | optional_count=0
[Flow] selection → prompt-build | selected_count=3
[Flow] model(local) | provider=ollama model=qwen3:14b
[Flow] final provider=local
[Flow] model → response | response_chars=3909
[Memory-Write] stored_length=3909 chars domain=build memory_type=reference
```

Result:

```text
Returned a structured build roadmap and correctly used BuildAgent while preserving local-first routing.
```

Outcome:

```text
PASS
```

## Final Recommendation

Keep only the `app/agents/router.py` change.

Do not remove `"assistant"` from the build-domain keyword list in `app/llm/service.py`; that change is unnecessary once `route_request()` stops injecting the executive prompt wrapper.

Recommended next step:

```text
Commit app/agents/router.py after review.
```
