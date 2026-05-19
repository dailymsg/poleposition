from typing import Protocol

from openai_prompt.integrations.llm.schemas import LLMTextResult


class LLMProvider(Protocol):
    def generate_text(self, *, system_prompt: str, user_prompt: str) -> LLMTextResult:
        ...
