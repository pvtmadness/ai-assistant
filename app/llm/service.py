"""
SYSTEM ARCHITECTURE NOTES

Pipeline:
prompt → router → model → memory → response

Model roles:
- mistral → fast local model
- qwen3:14b → complex local model
- OpenAI (gpt-4.1-mini) → remote fallback / escalation

Routing:
- router.classify() decides simple vs complex
- ask() maps that to local models by default

Escalation:
- local model always runs first
- _should_escalate() decides if response quality is insufficient
- if triggered → escalate to OpenAI model

IMPORTANT:
- router reasoning model (qwen) is LOCAL
- escalation model (OpenAI) must be explicitly constructed
- do NOT use router.get_reasoning_profile() for escalation
"""

from app.memory.store import MemoryStore
from app.llm.router import LLMProvider, ModelProfile

import uuid
from app.memory.logger import ConversationLogger
from app.llm.router import LLMRouter, TaskType
from app.llm.client import LLMClient
from app.config.settings import settings
from app.memory.logger import ConversationLogger
import requests

class LLMService:
    def __init__(self) -> None:
        self.router = LLMRouter(
            fast_model=settings.default_fast_model,
            reasoning_model=settings.reasoning_model,
        )
        self.client = LLMClient()
        self.logger = ConversationLogger()
        self.memory = MemoryStore()

    def run(self, task_type: str, prompt: str):
        if task_type == "fast":
            profile = self.router.get_fast_profile()

        elif task_type == "reasoning":
            profile = self.router.get_reasoning_profile()

        else:
            raise ValueError("Unsupported task type")

        print(f"[Service] task_type={task_type}, profile={profile}")
        response = self.client.run(profile, prompt)
        content = response.content
    
        #log
        self.logger.append(prompt, content)
        
        # store in vector DB
        self._write_memory(prompt, content, memory_id=str(uuid.uuid4()))

        return content
    
    def _call_ollama(self, model, prompt):
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload)
        return response.json()["response"] 

    def _should_escalate(self, answer, task_type):
        if task_type != TaskType.REASONING:
            return False

        answer_lower = answer.lower()
        length = len(answer.strip())

        # --- RULE 1: too short ---
        if length < 300:
            return True

        # --- RULE 2: weak / uncertain language ---
        weak_signals = [
            "i'm not sure",
            "i am not sure",
            "insufficient information",
            "not enough information",
            "cannot determine",
            "unclear",
            "it depends"
        ]

        if any(signal in answer_lower for signal in weak_signals):
            return True

        # --- RULE 3: obvious non-answer / refusal ---
        non_answer_signals = [
            "i can't answer",
            "i cannot answer",
            "i can't help with that",
            "i cannot help with that",
            "as an ai language model",
            "i don't have access",
            "no answer",
            "error:",
            "exception:"
        ]

        if any(signal in answer_lower for signal in non_answer_signals):
            return True

        return False

    def _detect_domain(self, prompt: str) -> str:
        prompt_lower = prompt.lower()

        domain_keywords = {
            "trading": [
                "atr",
                "breakout",
                "candle",
                "futures",
                "hvn",
                "lvn",
                "market profile",
                "order flow",
                "price action",
                "resistance",
                "support",
                "trade",
                "trading",
                "volume profile",
                "vwap",
            ],
            "medicine": [
                "diagnosis",
                "disease",
                "doctor",
                "health",
                "medical",
                "medicine",
                "patient",
                "prescription",
                "symptom",
                "treatment",
            ],
            "build": [
                "api",
                "app",
                "architecture",
                "build",
                "code",
                "deploy",
                "implementation",
                "refactor",
                "repo",
                "service",
                "software",
                "test",
            ],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return domain

        return "general"

    def _classify_memory_type(self, prompt: str, answer: str, domain: str) -> str:
        prompt_lower = prompt.lower()
        answer_lower = answer.lower()
        combined = f"{prompt_lower}\n{answer_lower}"
        answer_length = len(answer.strip())

        authoritative_markers = [
            "architecture decision",
            "design decision",
            "decision:",
            "we decided",
            "use this rule",
            "always",
            "never",
            "prefer",
            "user prefers",
            "my preference",
            "durable rule",
            "heuristic",
            "playbook",
        ]

        if any(marker in combined for marker in authoritative_markers):
            return "authoritative"

        if domain == "trading" and any(
            marker in combined
            for marker in [
                "trading rule",
                "entry rule",
                "exit rule",
                "risk rule",
                "stop-loss rule",
                "position sizing",
            ]
        ):
            return "authoritative"

        if domain == "medicine" and any(
            marker in combined
            for marker in [
                "medical heuristic",
                "clinical heuristic",
                "diagnostic heuristic",
                "treatment protocol",
                "red flag",
            ]
        ):
            return "authoritative"

        if answer_length < 500:
            return "ephemeral"

        reference_markers = [
            "summary",
            "explanation",
            "definition",
            "framework",
            "steps",
            "guide",
            "overview",
            "key applications",
            "core functions",
        ]

        if domain != "general" and any(marker in combined for marker in reference_markers):
            return "reference"

        if answer_length >= 900 and domain != "general":
            return "reference"

        return "ephemeral"

    def _write_memory(
        self,
        prompt: str,
        content: str,
        memory_id: str | None = None,
        domain: str | None = None,
    ) -> str:
        domain = domain or self._detect_domain(prompt)
        memory_type = self._classify_memory_type(prompt, content, domain)

        if memory_type == "ephemeral":
            print(f"[Memory-Write] skipped memory_type=ephemeral domain={domain}")
            return memory_type

        self.memory.add(
            content,
            memory_id=memory_id,
            domain=domain,
            memory_type=memory_type,
        )
        print(
            f"[Memory-Write] stored_length={len(content)} chars "
            f"domain={domain} memory_type={memory_type}"
        )

        return memory_type
      
    def ask(self, prompt, model=None):
        # --- STEP 1: ROUTE TASK ---
        if model:
            selected_model = model
        else:
            route = self.router.classify(prompt)
            if route == "simple":
                selected_model = "mistral"
            else:
                selected_model = "qwen3:14b"

        route = "simple" if selected_model == "mistral" else "complex"
        print(f"[Flow] prompt → router → model | route={route} model={selected_model}")
        domain = self._detect_domain(prompt)
        print(f"[Flow] domain detected | domain={domain}")

        # --- STEP 2/3: MEMORY RETRIEVAL ---
        background_memories = []
        if route == "simple":
            authoritative_memories = []
            reference_memories = []
            selected_semantic = []

            print("[Flow] simple route → memory skipped")

        else:
            if domain == "general":
                authoritative_memories = []
                reference_memories = self.memory.search(
                    prompt,
                    limit=3,
                    memory_type="reference",
                )
                semantic_results = reference_memories
                print(f"[Flow] router → memory/tools | domain=general reference_count={len(reference_memories)}")
            else:
                authoritative_memories = self.memory.search(
                    prompt,
                    limit=2,
                    domain=domain,
                    memory_type="authoritative",
                )
                reference_memories = self.memory.search(
                    prompt,
                    limit=3,
                    domain=domain,
                    memory_type="reference",
                )
                background_results = self.memory.search(
                    prompt,
                    limit=3,
                    memory_type="reference",
                )
                semantic_results = authoritative_memories + reference_memories
                print(
                    f"[Flow] router → memory/tools | domain={domain} "
                    f"authoritative_count={len(authoritative_memories)} "
                    f"reference_count={len(reference_memories)}"
                )

                same_domain_seen = set(semantic_results)
                background_memories = [
                    memory for memory in background_results if memory not in same_domain_seen
                ][:1]
                print(f"[Flow] memory/tools → background | optional_count={len(background_memories)}")

            selected_semantic = semantic_results[:3]

            print(f"[Flow] selection → prompt-build | selected_count={len(selected_semantic)}")

        # --- STEP 4: BUILD CONTEXT ---
        trimmed_authoritative = authoritative_memories[:2]
        trimmed_reference = reference_memories[:2]
        trimmed_background = background_memories[:1]

        memory_sections = []
        if trimmed_authoritative:
            memory_sections.append(
                f"Authoritative same-domain memory context ({domain}):\n"
                + "\n".join(trimmed_authoritative)
            )
        if trimmed_reference:
            label = "Reference same-domain memory context"
            if domain == "general":
                label = "Optional reference memory context"
            memory_sections.append(
                f"{label} ({domain}):\n" + "\n".join(trimmed_reference)
            )
        if trimmed_background:
            memory_sections.append(
                "Optional cross-domain background memory:\n" + "\n".join(trimmed_background)
            )

        memory_context = "\n\n".join(memory_sections)

        if route == "simple" or not memory_context.strip():
            full_prompt = prompt
        else:
            full_prompt = f"""Relevant memory:
{memory_context}

User request:
{prompt}
"""

        # --- STEP 5: MODEL CALL ---
        if selected_model in ["mistral", "qwen3:14b"]:
            print(f"[Flow] model(local) | provider=ollama model={selected_model}")
            content = self._call_ollama(selected_model, full_prompt).strip()

            # --- OPTIONAL ESCALATION ---
            if self._should_escalate(
                content,
                TaskType.REASONING if route == "complex" else TaskType.FAST,
            ):
                print("[Flow] escalation triggered → remote model")

                profile = ModelProfile(
                    provider=LLMProvider.OPENAI,
                    model_name=settings.default_fast_model,
                    purpose="escalation",
                )

                enhanced_prompt = f"""
You are an expert assistant.

The user request was:
{prompt}

Your task:
- Provide a precise, fully developed answer
- Avoid generic summaries
- Be specific and actionable
- Match the domain of the question

Include:
- Clear structure
- Concrete details
- If applicable, step-by-step logic or rules

Context from memory, which may or may not be relevant:
{memory_context}
"""

                response = self.client.run(profile, enhanced_prompt)
                content = response.content.strip()
                print("[Flow] final provider=remote")
            else:
                print("[Flow] final provider=local")

        else:
            print(f"[Flow] model(remote) | provider=openai model={selected_model}")

            profile = ModelProfile(
                provider=LLMProvider.OPENAI,
                model_name=selected_model,
                purpose="direct-remote",
            )

            response = self.client.run(profile, full_prompt)
            content = response.content.strip()

        print(f"[Flow] model → response | response_chars={len(content)}")

        # --- STEP 6: OPTIONAL PARALLEL SIGNAL ---
        parallel_note = ""
        if route == "complex" and selected_semantic:
            keywords = prompt.lower().split()
            for mem in selected_semantic:
                if any(k in mem.lower() for k in keywords):
                    parallel_note = "Parallel: related prior pattern detected.\n\n"
                    print("[Parallel] triggered")
                    break

        final_output = f"{parallel_note}{content}"

        # --- STEP 7: STORE MEMORY ---
        clean_content = content.replace("Parallel: related prior pattern detected.\n\n", "")
        self._write_memory(prompt, clean_content, domain=domain)

        return final_output
