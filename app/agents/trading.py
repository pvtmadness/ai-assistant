from app.agents.base import BaseAgent


class TradingAgent(BaseAgent):
    domain = "trading"
    name = "TradingAgent"

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

        return f"""Trading context:
{chr(10).join(memory_sections)}

User request:
{user_prompt}
"""
