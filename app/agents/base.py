from abc import ABC


class BaseAgent(ABC):
    domain = "general"
    name = "DefaultAgent"

    def should_handle(self, prompt: str) -> bool:
        return True

    def preferred_task_type(self, prompt: str) -> str | None:
        return None

    def classify_memory_type(self, prompt: str, answer: str) -> str | None:
        return None

    def build_prompt(
        self,
        user_prompt: str,
        authoritative_memory: list[str],
        reference_memory: list[str],
        background_memory: list[str],
    ) -> str:
        memory_sections = self._memory_sections(
            authoritative_memory=authoritative_memory,
            reference_memory=reference_memory,
            background_memory=background_memory,
        )

        if not memory_sections:
            return user_prompt

        return f"""Relevant memory:
{chr(10).join(memory_sections)}

User request:
{user_prompt}
"""

    def _memory_sections(
        self,
        authoritative_memory: list[str],
        reference_memory: list[str],
        background_memory: list[str],
    ) -> list[str]:
        sections = []

        if authoritative_memory:
            sections.append(
                f"Authoritative same-domain memory context ({self.domain}):\n"
                + "\n".join(authoritative_memory)
            )
        if reference_memory:
            label = "Reference same-domain memory context"
            if self.domain == "general":
                label = "Optional reference memory context"
            sections.append(f"{label} ({self.domain}):\n" + "\n".join(reference_memory))
        if background_memory:
            sections.append(
                "Optional cross-domain background memory:\n"
                + "\n".join(background_memory)
            )

        return sections


class DefaultAgent(BaseAgent):
    domain = "general"
    name = "DefaultAgent"
