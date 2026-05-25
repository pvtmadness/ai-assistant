from dataclasses import dataclass

from openai import OpenAI

from app.config.settings import settings
from app.llm.router import LLMProvider, ModelProfile


@dataclass(frozen=True)
class LLMResponse:
    provider: str
    model: str
    content: str


class LLMClient:
    def run(self, profile: ModelProfile, prompt: str) -> LLMResponse:
        if profile.provider == LLMProvider.OPENAI:
            return self._run_openai(profile, prompt)

        raise ValueError(f"Unsupported provider: {profile.provider.value}")

    def _run_openai(self, profile: ModelProfile, prompt: str) -> LLMResponse:
        client = OpenAI(api_key=settings.openai_api_key)

        response = client.responses.create(
            model=profile.model_name,
            input=prompt,
        )

        content = response.output_text or ""

        return LLMResponse(
            provider=profile.provider.value,
            model=profile.model_name,
            content=content,
        )