"""
SYSTEM ARCHITECTURE NOTES

Purpose:
- This file defines model profiles and the routing layer.
- It decides which class of model a task should use.
- It does NOT execute model calls.

Pipeline role:
prompt → router → model → memory → response

Router responsibilities:
- classify work as FAST or REASONING
- return model profiles for those roles
- keep provider/model metadata together

Current model roles:
- FAST profile:
    provider = LOCAL
    model = mistral
    purpose = fast local response

- REASONING profile:
    provider = LOCAL
    model = qwen3:14b
    purpose = complex local response

- ROUTING profile:
    provider = OPENAI
    model = gpt-4.1-mini
    purpose = optional classifier / future routing support

Important distinctions:
- "REASONING" in this file currently means the stronger LOCAL model, not OpenAI.
- OpenAI fallback / escalation is handled in service.py, not here.
- Do NOT assume get_reasoning_profile() returns a remote model.
- If remote escalation is needed, service.py must construct an explicit OPENAI profile.

Design rule:
- router.py chooses model role
- service.py decides whether to stay local or escalate remote
"""

from enum import Enum
from dataclasses import dataclass


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GROK = "grok"
    LOCAL = "local"


@dataclass(frozen=True)
class ModelProfile:
    provider: LLMProvider
    model_name: str
    purpose: str


class TaskType(str, Enum):
    FAST = "fast"
    REASONING = "reasoning"


class LLMRouter:
    def __init__(self, fast_model: str, reasoning_model: str) -> None:
        self.fast_model = fast_model
        self.reasoning_model = reasoning_model

    def get_fast_profile(self) -> ModelProfile:
        return ModelProfile(
            provider=LLMProvider.LOCAL,
            model_name=self.fast_model,
            purpose="fast",
        )

    def get_reasoning_profile(self) -> ModelProfile:
        return ModelProfile(
            provider=LLMProvider.LOCAL,
            model_name=self.reasoning_model,
            purpose="reasoning",
        )
    
    def get_routing_profile(self) ->ModelProfile:
        return ModelProfile(
            provider=LLMProvider.OPENAI,
            model_name=self.fast_model,
            purpose="routing",
        )

    def route(self, task_type: TaskType = TaskType.FAST) -> ModelProfile:
        if task_type == TaskType.REASONING:
            return self.get_reasoning_profile()
        return self.get_fast_profile()
    
    def classify(self, prompt: str) -> str:
        prompt_lower = prompt.lower()

        complex_keywords = [
            "analyze",
            "compare",
            "design",
            "create",
            "build",
            "strategy",
            "system",
            "architecture",
            "plan",
            "reason",
            "why",
        ]

        if len(prompt) > 50 or any(word in prompt_lower for word in complex_keywords):
            return "complex"

        return "simple"
