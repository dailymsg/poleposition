from dataclasses import dataclass

from openai_prompt.integrations.llm.schemas import LLMTextResult


@dataclass(slots=True)
class AnthropicProvider:
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

        raise NotImplementedError(
            "Install an Anthropic-compatible SDK or implement the adapter in "
            f"{__file__} for your preferred provider workflow."
        )
