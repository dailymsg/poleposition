from dataclasses import dataclass
from typing import Any

from openai_prompt.integrations.llm.schemas import LLMTextResult


@dataclass(slots=True)
class OpenAIProvider:
    model: str
    api_key: str
    base_url: str | None = None
    timeout_seconds: float = 30.0
    temperature: float = 0.2
    max_tokens: int | None = None

    def generate_text(self, *, system_prompt: str, user_prompt: str) -> LLMTextResult:
        if not self.api_key:
            raise RuntimeError(
                "Set LLM_API_KEY in .env before using the ai-prompt template."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI prompt example requires the OpenAI SDK. Run `uv sync --extra dev`."
            ) from exc

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url or None,
            timeout=self.timeout_seconds,
        )
        request: dict[str, Any] = {
            "model": self.model,
            "instructions": system_prompt,
            "input": user_prompt,
            "temperature": self.temperature,
        }
        if self.max_tokens is not None:
            request["max_output_tokens"] = self.max_tokens

        response = client.responses.create(**request)
        return LLMTextResult(
            text=response.output_text,
            provider="openai",
            model=self.model,
        )
