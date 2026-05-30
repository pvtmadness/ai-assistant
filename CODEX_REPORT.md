# Codex Report

## Objective

Implement memory write filtering so the assistant does not store every response as durable memory. Add memory types (`authoritative`, `reference`, `ephemeral`), store memory metadata with `domain` and `memory_type`, skip ephemeral writes by default, and retrieve memory in priority order while preserving local-first model behavior.

## Files Changed

- `app/llm/service.py`
- `app/memory/store.py`
- `CODEX_REPORT.md`

## Full Diff

```diff
diff --git a/app/llm/service.py b/app/llm/service.py
index cef4f37..6b446a4 100644
--- a/app/llm/service.py
+++ b/app/llm/service.py
@@ -63,8 +63,7 @@ class LLMService:
         self.logger.append(prompt, content)
         
         # store in vector DB
-        memory_text = content
-        self.memory.add(memory_text, str(uuid.uuid4()), domain=self._detect_domain(prompt))
+        self._write_memory(prompt, content, memory_id=str(uuid.uuid4()))
 
         return content
     
@@ -177,6 +176,106 @@ class LLMService:
                 return domain
 
         return "general"
+
+    def _classify_memory_type(self, prompt: str, answer: str, domain: str) -> str:
+        prompt_lower = prompt.lower()
+        answer_lower = answer.lower()
+        combined = f"{prompt_lower}\n{answer_lower}"
+        answer_length = len(answer.strip())
+
+        authoritative_markers = [
+            "architecture decision",
+            "design decision",
+            "decision:",
+            "we decided",
+            "use this rule",
+            "always",
+            "never",
+            "prefer",
+            "user prefers",
+            "my preference",
+            "durable rule",
+            "heuristic",
+            "playbook",
+        ]
+
+        if any(marker in combined for marker in authoritative_markers):
+            return "authoritative"
+
+        if domain == "trading" and any(
+            marker in combined
+            for marker in [
+                "trading rule",
+                "entry rule",
+                "exit rule",
+                "risk rule",
+                "stop-loss rule",
+                "position sizing",
+            ]
+        ):
+            return "authoritative"
+
+        if domain == "medicine" and any(
+            marker in combined
+            for marker in [
+                "medical heuristic",
+                "clinical heuristic",
+                "diagnostic heuristic",
+                "treatment protocol",
+                "red flag",
+            ]
+        ):
+            return "authoritative"
+
+        if answer_length < 500:
+            return "ephemeral"
+
+        reference_markers = [
+            "summary",
+            "explanation",
+            "definition",
+            "framework",
+            "steps",
+            "guide",
+            "overview",
+            "key applications",
+            "core functions",
+        ]
+
+        if domain != "general" and any(marker in combined for marker in reference_markers):
+            return "reference"
+
+        if answer_length >= 900 and domain != "general":
+            return "reference"
+
+        return "ephemeral"
+
+    def _write_memory(
+        self,
+        prompt: str,
+        content: str,
+        memory_id: str | None = None,
+        domain: str | None = None,
+    ) -> str:
+        domain = domain or self._detect_domain(prompt)
+        memory_type = self._classify_memory_type(prompt, content, domain)
+
+        if memory_type == "ephemeral":
+            print(f"[Memory-Write] skipped memory_type=ephemeral domain={domain}")
+            return memory_type
+
+        self.memory.add(
+            content,
+            memory_id=memory_id,
+            domain=domain,
+            memory_type=memory_type,
+        )
+        print(
+            f"[Memory-Write] stored_length={len(content)} chars "
+            f"domain={domain} memory_type={memory_type}"
+        )
+
+        return memory_type
       
     def ask(self, prompt, model=None):
         # --- STEP 1: ROUTE TASK ---
@@ -194,56 +293,78 @@ class LLMService:
         domain = self._detect_domain(prompt)
         print(f"[Flow] domain detected | domain={domain}")
 
-                # --- STEP 2/3: MEMORY RETRIEVAL ---
+        # --- STEP 2/3: MEMORY RETRIEVAL ---
         background_memories = []
         if route == "simple":
-            recent_memories = []
+            authoritative_memories = []
+            reference_memories = []
             selected_semantic = []
 
             print("[Flow] simple route → memory skipped")
 
         else:
             if domain == "general":
-                recent_memories = self.memory.get_recent(limit=3)
-                semantic_results = self.memory.search(prompt, limit=5)
-                print(f"[Flow] router → memory/tools | domain=general recent_count={len(recent_memories)}")
-                print(f"[Flow] memory/tools → selection | semantic_raw={len(semantic_results)}")
+                authoritative_memories = []
+                reference_memories = self.memory.search(
+                    prompt,
+                    limit=3,
+                    memory_type="reference",
+                )
+                semantic_results = reference_memories
+                print(f"[Flow] router → memory/tools | domain=general reference_count={len(reference_memories)}")
             else:
-                recent_memories = self.memory.get_recent(limit=3, domain=domain)
-                semantic_results = self.memory.search(prompt, limit=5, domain=domain)
-                background_results = self.memory.search(prompt, limit=3)
-                print(f"[Flow] router → memory/tools | domain={domain} recent_count={len(recent_memories)}")
-                print(f"[Flow] memory/tools → selection | same_domain_raw={len(semantic_results)}")
+                authoritative_memories = self.memory.search(
+                    prompt,
+                    limit=2,
+                    domain=domain,
+                    memory_type="authoritative",
+                )
+                reference_memories = self.memory.search(
+                    prompt,
+                    limit=3,
+                    domain=domain,
+                    memory_type="reference",
+                )
+                background_results = self.memory.search(
+                    prompt,
+                    limit=3,
+                    memory_type="reference",
+                )
+                semantic_results = authoritative_memories + reference_memories
+                print(
+                    f"[Flow] router → memory/tools | domain={domain} "
+                    f"authoritative_count={len(authoritative_memories)} "
+                    f"reference_count={len(reference_memories)}"
+                )
 
-                same_domain_seen = set(recent_memories + semantic_results)
+                same_domain_seen = set(semantic_results)
                 background_memories = [
                     memory for memory in background_results if memory not in same_domain_seen
                 ][:1]
                 print(f"[Flow] memory/tools → background | optional_count={len(background_memories)}")
 
-            top_semantic = semantic_results[:2]
-            loose_semantic = semantic_results[2:3]
-            selected_semantic = top_semantic + loose_semantic
+            selected_semantic = semantic_results[:3]
 
             print(f"[Flow] selection → prompt-build | selected_count={len(selected_semantic)}")
 
         # --- STEP 4: BUILD CONTEXT ---
-        trimmed_recent = recent_memories[:2]
-        trimmed_semantic = selected_semantic[:2]
+        trimmed_authoritative = authoritative_memories[:2]
+        trimmed_reference = reference_memories[:2]
         trimmed_background = background_memories[:1]
 
-        combined_memories = trimmed_recent + trimmed_semantic
         memory_sections = []
-        if combined_memories:
+        if trimmed_authoritative:
+            memory_sections.append(
+                f"Authoritative same-domain memory context ({domain}):\n"
+                + "\n".join(trimmed_authoritative)
+            )
+        if trimmed_reference:
+            label = "Reference same-domain memory context"
             if domain == "general":
-                memory_sections.append(
-                    "Optional background memory context:\n" + "\n".join(combined_memories)
-                )
-            else:
-                memory_sections.append(
-                    f"Authoritative same-domain memory context ({domain}):\n"
-                    + "\n".join(combined_memories)
-                )
+                label = "Optional reference memory context"
+            memory_sections.append(
+                f"{label} ({domain}):\n" + "\n".join(trimmed_reference)
+            )
         if trimmed_background:
             memory_sections.append(
                 "Optional cross-domain background memory:\n" + "\n".join(trimmed_background)
@@ -334,7 +455,6 @@ Context from memory, which may or may not be relevant:
 
         # --- STEP 7: STORE MEMORY ---
         clean_content = content.replace("Parallel: related prior pattern detected.\n\n", "")
-        self.memory.add(clean_content, domain=domain)
-        print(f"[Memory-Write] stored_length={len(clean_content)} chars domain={domain}")
+        self._write_memory(prompt, clean_content, domain=domain)
 
         return final_output
diff --git a/app/memory/store.py b/app/memory/store.py
index 7037601..9794ae7 100644
--- a/app/memory/store.py
+++ b/app/memory/store.py
@@ -25,6 +25,7 @@ class MemoryStore:
         text: str,
         memory_id: str | None = None,
         domain: str = "general",
+        memory_type: str = "reference",
     ) -> None:
         if len(text) > 1200:
             text = text[:1200]
@@ -33,20 +34,41 @@ class MemoryStore:
             memory_id = str(uuid.uuid4())
 
         domain = (domain or "general").strip().lower()
+        memory_type = (memory_type or "reference").strip().lower()
         embedding = self.embedder.encode(text).tolist()
 
         self.collection.add(
             ids=[memory_id],
             documents=[text],
             embeddings=[embedding],
-            metadatas=[{"domain": domain}],
+            metadatas=[{"domain": domain, "memory_type": memory_type}],
         )
 
+    def _where(
+        self,
+        domain: str | None = None,
+        memory_type: str | None = None,
+    ) -> dict[str, Any] | None:
+        filters = []
+
+        if domain:
+            filters.append({"domain": domain.strip().lower()})
+        if memory_type:
+            filters.append({"memory_type": memory_type.strip().lower()})
+
+        if not filters:
+            return None
+        if len(filters) == 1:
+            return filters[0]
+
+        return {"$and": filters}
+
     def search(
         self,
         query: str,
         limit: int = 5,
         domain: str | None = None,
+        memory_type: str | None = None,
     ) -> list[str]:
         query_embedding = self.embedder.encode(query).tolist()
 
@@ -55,8 +77,9 @@ class MemoryStore:
             "n_results": limit,
         }
 
-        if domain:
-            query_args["where"] = {"domain": domain.strip().lower()}
+        where = self._where(domain=domain, memory_type=memory_type)
+        if where:
+            query_args["where"] = where
 
         results = self.collection.query(**query_args)
 
@@ -70,13 +93,15 @@ class MemoryStore:
         self,
         limit: int = 3,
         domain: str | None = None,
+        memory_type: str | None = None,
     ) -> list[str]:
         get_args: dict[str, Any] = {
             "include": ["documents", "metadatas"],
         }
 
-        if domain:
-            get_args["where"] = {"domain": domain.strip().lower()}
+        where = self._where(domain=domain, memory_type=memory_type)
+        if where:
+            get_args["where"] = where
 
         results = self.collection.get(**get_args)
 
@@ -90,13 +115,23 @@ class MemoryStore:
         self,
         query: str,
         domain: str | None = None,
+        memory_type: str | None = None,
         recent_limit: int = 3,
         semantic_limit: int = 2,
         loose_limit: int = 1,
         max_total: int = 3,
     ) -> list[str]:
-        recent_docs = self.get_recent(limit=recent_limit, domain=domain)
-        semantic_docs = self.search(query=query, limit=semantic_limit, domain=domain)
+        recent_docs = self.get_recent(
+            limit=recent_limit,
+            domain=domain,
+            memory_type=memory_type,
+        )
+        semantic_docs = self.search(
+            query=query,
+            limit=semantic_limit,
+            domain=domain,
+            memory_type=memory_type,
+        )
         loose_docs = self.search(query=query, limit=loose_limit)
 
         combined: list[str] = []
```

## Verification Output

### Syntax Check

```text
venv/bin/python -m py_compile app/llm/service.py app/memory/store.py
```

Result: completed with no output/errors.

### VWAP Prompt

Prompt:

```text
What is VWAP and how is it used with volume profile?
```

Observed:

```text
[Flow] domain detected | domain=trading
[Flow] final provider=local
[Memory-Write] stored_length=891 chars domain=trading memory_type=reference
```

### Build/Architecture Prompt

Prompt:

```text
Architecture decision: For this app, prefer storing durable memory metadata with domain and memory_type fields. Summarize this build decision.
```

Observed:

```text
[Flow] domain detected | domain=build
[Flow] final provider=local
[Memory-Write] stored_length=658 chars domain=build memory_type=authoritative
```

### Agent Framework Prompt

Prompt:

```text
How should I structure the agent framework for this local AI assistant?
```

Observed:

```text
[Flow] domain detected | domain=general
[Flow] final provider=local
[Memory-Write] skipped memory_type=ephemeral domain=general
```

## Git Status

```text
## master...origin/master
 M app/llm/service.py
 M app/memory/store.py
?? CODEX_REPORT.md
```

## Remaining Concerns

- The prompt `How should I structure the agent framework for this local AI assistant?` currently detects as `general`, not `build`, because the build domain keyword list does not include terms like `agent`, `framework`, or `assistant`.
- Existing memories written before `memory_type` was introduced do not have `memory_type` metadata and will not match typed retrieval filters unless migrated or re-written.
- The memory classifier is intentionally rule-based and simple; it may misclassify borderline answers until the heuristics are expanded.
- Cross-domain background retrieval currently only pulls `reference` memories and uses document text de-duplication, not metadata-rich scoring.
