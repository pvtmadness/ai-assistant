from pathlib import Path

from app.agents.base import BaseAgent


class BuildAgent(BaseAgent):
    domain = "build"
    name = "BuildAgent"
    project_brief_path = Path("docs/PROJECT_BRIEF.md")

    def preferred_task_type(self, prompt: str) -> str | None:
        prompt_lower = prompt.lower()
        if any(
            marker in prompt_lower
            for marker in ["architecture", "design", "framework", "system"]
        ):
            return "reasoning"

        return None

    def _load_project_brief(self) -> tuple[str, str | None]:
        try:
            return self.project_brief_path.read_text(encoding="utf-8").strip(), None
        except OSError as exc:
            return "", f"Project brief unavailable: {exc}"

    def build_prompt(
        self,
        user_prompt: str,
        authoritative_memory: list[str],
        reference_memory: list[str],
        background_memory: list[str],
    ) -> str:
        project_brief, project_brief_warning = self._load_project_brief()
        memory_sections = self._memory_sections(
            authoritative_memory=authoritative_memory,
            reference_memory=reference_memory,
            background_memory=background_memory,
        )
        context_sections = []

        if project_brief:
            context_sections.append(f"Project brief:\n{project_brief}")
        elif project_brief_warning:
            context_sections.append(project_brief_warning)

        context_sections.extend(memory_sections)

        if not context_sections:
            return user_prompt

        return f"""Build context:
{chr(10).join(context_sections)}

User request:
{user_prompt}
"""
