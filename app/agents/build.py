from app.agents.base import BaseAgent


class BuildAgent(BaseAgent):
    domain = "build"
    name = "BuildAgent"

    def preferred_task_type(self, prompt: str) -> str | None:
        prompt_lower = prompt.lower()
        if any(
            marker in prompt_lower
            for marker in ["architecture", "design", "framework", "system"]
        ):
            return "reasoning"

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

        return f"""Build context:
{chr(10).join(memory_sections)}

User request:
{user_prompt}
"""
