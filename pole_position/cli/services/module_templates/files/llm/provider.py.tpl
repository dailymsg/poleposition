from typing import Protocol

from {{package_name}}.integrations.llm.schemas import LLMTextResult


class LLMProvider(Protocol):
    def generate_text(self, *, system_prompt: str, user_prompt: str) -> LLMTextResult:
        ...
