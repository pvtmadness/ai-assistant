# Codex Report

## Objective

Implement the approved first phase of the agent framework:

1. Add `app/agents/base.py`
2. Add `DefaultAgent`
3. Add `TradingAgent`
4. Add `MedicalAgent`
5. Add `BuildAgent`
6. Add `AgentRegistry`

The implementation preserves current behavior by keeping `LLMService` responsible for memory retrieval, model calls, escalation, and memory writes. Agents only shape prompts and expose optional hints.

## Files Changed

- `app/agents/base.py`
- `app/agents/trading.py`
- `app/agents/medical.py`
- `app/agents/build.py`
- `app/agents/registry.py`
- `app/llm/service.py`
- `CODEX_REPORT.md`

Existing untracked design document still present:

- `AGENT_FRAMEWORK_DESIGN.md`

## Full Diff

```diff
diff --git a/app/agents/base.py b/app/agents/base.py
new file mode 100644
--- /dev/null
+++ b/app/agents/base.py
@@ -0,0 +1,65 @@
+from abc import ABC
+
+
+class BaseAgent(ABC):
+    domain = "general"
+    name = "DefaultAgent"
+
+    def should_handle(self, prompt: str) -> bool:
+        return True
+
+    def preferred_task_type(self, prompt: str) -> str | None:
+        return None
+
+    def classify_memory_type(self, prompt: str, answer: str) -> str | None:
+        return None
+
+    def build_prompt(
+        self,
+        user_prompt: str,
+        authoritative_memory: list[str],
+        reference_memory: list[str],
+        background_memory: list[str],
+    ) -> str:
+        memory_sections = self._memory_sections(
+            authoritative_memory=authoritative_memory,
+            reference_memory=reference_memory,
+            background_memory=background_memory,
+        )
+
+        if not memory_sections:
+            return user_prompt
+
+        return f"""Relevant memory:
+{chr(10).join(memory_sections)}
+
+User request:
+{user_prompt}
+"""
+
+    def _memory_sections(
+        self,
+        authoritative_memory: list[str],
+        reference_memory: list[str],
+        background_memory: list[str],
+    ) -> list[str]:
+        sections = []
+
+        if authoritative_memory:
+            sections.append(
+                f"Authoritative same-domain memory context ({self.domain}):\n"
+                + "\n".join(authoritative_memory)
+            )
+        if reference_memory:
+            label = "Reference same-domain memory context"
+            if self.domain == "general":
+                label = "Optional reference memory context"
+            sections.append(f"{label} ({self.domain}):\n" + "\n".join(reference_memory))
+        if background_memory:
+            sections.append(
+                "Optional cross-domain background memory:\n"
+                + "\n".join(background_memory)
+            )
+
+        return sections
+
+
+class DefaultAgent(BaseAgent):
+    domain = "general"
+    name = "DefaultAgent"
diff --git a/app/agents/trading.py b/app/agents/trading.py
new file mode 100644
--- /dev/null
+++ b/app/agents/trading.py
@@ -0,0 +1,25 @@
+from app.agents.base import BaseAgent
+
+
+class TradingAgent(BaseAgent):
+    domain = "trading"
+    name = "TradingAgent"
+
+    def build_prompt(
+        self,
+        user_prompt: str,
+        authoritative_memory: list[str],
+        reference_memory: list[str],
+        background_memory: list[str],
+    ) -> str:
+        memory_sections = self._memory_sections(
+            authoritative_memory=authoritative_memory,
+            reference_memory=reference_memory,
+            background_memory=background_memory,
+        )
+
+        if not memory_sections:
+            return user_prompt
+
+        return f"""Trading context:
+{chr(10).join(memory_sections)}
+
+User request:
+{user_prompt}
+"""
diff --git a/app/agents/medical.py b/app/agents/medical.py
new file mode 100644
--- /dev/null
+++ b/app/agents/medical.py
@@ -0,0 +1,27 @@
+from app.agents.base import BaseAgent
+
+
+class MedicalAgent(BaseAgent):
+    domain = "medicine"
+    name = "MedicalAgent"
+
+    def build_prompt(
+        self,
+        user_prompt: str,
+        authoritative_memory: list[str],
+        reference_memory: list[str],
+        background_memory: list[str],
+    ) -> str:
+        memory_sections = self._memory_sections(
+            authoritative_memory=authoritative_memory,
+            reference_memory=reference_memory,
+            background_memory=background_memory,
+        )
+
+        if not memory_sections:
+            return user_prompt
+
+        return f"""Medical context:
+Use memory as educational context, not as a diagnosis.
+
+{chr(10).join(memory_sections)}
+
+User request:
+{user_prompt}
+"""
diff --git a/app/agents/build.py b/app/agents/build.py
new file mode 100644
--- /dev/null
+++ b/app/agents/build.py
@@ -0,0 +1,35 @@
+from app.agents.base import BaseAgent
+
+
+class BuildAgent(BaseAgent):
+    domain = "build"
+    name = "BuildAgent"
+
+    def preferred_task_type(self, prompt: str) -> str | None:
+        prompt_lower = prompt.lower()
+        if any(
+            marker in prompt_lower
+            for marker in ["architecture", "design", "framework", "system"]
+        ):
+            return "reasoning"
+
+        return None
+
+    def build_prompt(
+        self,
+        user_prompt: str,
+        authoritative_memory: list[str],
+        reference_memory: list[str],
+        background_memory: list[str],
+    ) -> str:
+        memory_sections = self._memory_sections(
+            authoritative_memory=authoritative_memory,
+            reference_memory=reference_memory,
+            background_memory=background_memory,
+        )
+
+        if not memory_sections:
+            return user_prompt
+
+        return f"""Build context:
+{chr(10).join(memory_sections)}
+
+User request:
+{user_prompt}
+"""
diff --git a/app/agents/registry.py b/app/agents/registry.py
new file mode 100644
--- /dev/null
+++ b/app/agents/registry.py
@@ -0,0 +1,29 @@
+from app.agents.base import BaseAgent, DefaultAgent
+from app.agents.build import BuildAgent
+from app.agents.medical import MedicalAgent
+from app.agents.trading import TradingAgent
+
+
+class AgentRegistry:
+    def __init__(self) -> None:
+        self.default_agent = DefaultAgent()
+        self._agents: dict[str, BaseAgent] = {}
+
+    def register(self, agent: BaseAgent) -> None:
+        self._agents[agent.domain] = agent
+
+    def get(self, domain: str) -> BaseAgent:
+        return self._agents.get(domain, self.default_agent)
+
+    def resolve(self, prompt: str, domain: str) -> BaseAgent:
+        agent = self.get(domain)
+        if agent.should_handle(prompt):
+            return agent
+
+        return self.default_agent
+
+
+def create_default_agent_registry() -> AgentRegistry:
+    registry = AgentRegistry()
+    registry.register(TradingAgent())
+    registry.register(MedicalAgent())
+    registry.register(BuildAgent())
+    return registry
diff --git a/app/llm/service.py b/app/llm/service.py
index 6c446ce..fa09d92 100644
--- a/app/llm/service.py
+++ b/app/llm/service.py
@@ -24,6 +24,7 @@ IMPORTANT:
 - do NOT use router.get_reasoning_profile() for escalation
 """
 
+from app.agents.registry import create_default_agent_registry
 from app.memory.store import MemoryStore
 from app.llm.router import LLMProvider, ModelProfile
 
@@ -44,6 +45,7 @@ class LLMService:
         self.client = LLMClient()
         self.logger = ConversationLogger()
         self.memory = MemoryStore()
+        self.agent_registry = create_default_agent_registry()
 
     def run(self, task_type: str, prompt: str):
         if task_type == "fast":
@@ -305,6 +307,8 @@ class LLMService:
         print(f"[Flow] prompt → router → model | route={route} model={selected_model}")
         domain = self._detect_domain(prompt)
         print(f"[Flow] domain detected | domain={domain}")
+        agent = self.agent_registry.resolve(prompt, domain)
+        print(f"[Flow] domain → agent | agent={agent.name}")
 
         # --- STEP 2/3: MEMORY RETRIEVAL ---
         background_memories = []
@@ -365,35 +369,13 @@ class LLMService:
         trimmed_reference = reference_memories[:2]
         trimmed_background = background_memories[:1]
 
-        memory_sections = []
-        if trimmed_authoritative:
-            memory_sections.append(
-                f"Authoritative same-domain memory context ({domain}):\n"
-                + "\n".join(trimmed_authoritative)
-            )
-        if trimmed_reference:
-            label = "Reference same-domain memory context"
-            if domain == "general":
-                label = "Optional reference memory context"
-            memory_sections.append(
-                f"{label} ({domain}):\n" + "\n".join(trimmed_reference)
-            )
-        if trimmed_background:
-            memory_sections.append(
-                "Optional cross-domain background memory:\n" + "\n".join(trimmed_background)
-            )
-
-        memory_context = "\n\n".join(memory_sections)
-
-        if route == "simple" or not memory_context.strip():
-            full_prompt = prompt
-        else:
-            full_prompt = f"""Relevant memory:
-{memory_context}
-
-User request:
-{prompt}
-"""
+        full_prompt = agent.build_prompt(
+            user_prompt=prompt,
+            authoritative_memory=trimmed_authoritative,
+            reference_memory=trimmed_reference,
+            background_memory=trimmed_background,
+        )
+        memory_context = full_prompt if full_prompt != prompt else ""
 
         # --- STEP 5: MODEL CALL ---
         if selected_model in ["mistral", "qwen3:14b"]:
```

## Verification Output

### Syntax Check

Command:

```text
venv/bin/python -m py_compile app/llm/service.py app/agents/base.py app/agents/trading.py app/agents/medical.py app/agents/build.py app/agents/registry.py
```

Result: completed with no output/errors.

### Trading Prompt

Prompt:

```text
What is VWAP and how is it used with volume profile?
```

Observed:

```text
[Flow] domain detected | domain=trading
[Flow] domain → agent | agent=TradingAgent
[Flow] model(local) | provider=ollama model=qwen3:14b
[Flow] final provider=local
```

### Medical Prompt

Prompt:

```text
What medical red flags should I know for chest pain?
```

Observed:

```text
[Flow] domain detected | domain=medicine
[Flow] domain → agent | agent=MedicalAgent
[Flow] model(local) | provider=ollama model=mistral
[Flow] final provider=local
```

### Build Prompt

Prompt:

```text
How should I structure the agent framework for this local AI assistant?
```

Observed:

```text
[Flow] domain detected | domain=build
[Flow] domain → agent | agent=BuildAgent
[Flow] model(local) | provider=ollama model=qwen3:14b
[Flow] final provider=local
```

## Git Status

```text
## master...origin/master
 M CODEX_REPORT.md
 M app/llm/service.py
?? AGENT_FRAMEWORK_DESIGN.md
?? app/agents/base.py
?? app/agents/build.py
?? app/agents/medical.py
?? app/agents/registry.py
?? app/agents/trading.py
```

## Remaining Concerns

- `AGENT_FRAMEWORK_DESIGN.md` remains untracked from the prior approved design-document step unless you want it included in a future commit.
- Agent hints are exposed but not consumed by model routing yet; this preserves current routing behavior.
- Prompt shaping is now delegated to agents, but memory retrieval, model calls, escalation, and memory writes remain in `LLMService`.
- No subdomain routing was added.
- `SpreadMatrixAgent`, `PortfolioAgent`, and `FunctionalMedicineAgent` were not added.
