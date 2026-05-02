from {{package_name}}.integrations.llm.factory import get_llm_provider
from {{package_name}}.integrations.llm.provider import LLMProvider
from {{package_name}}.modules.{{module_name}}.prompts import build_system_prompt
from {{package_name}}.modules.{{module_name}}.schemas import {{class_name}}PromptRequest, {{class_name}}PromptResponse


class {{class_name}}Orchestrator:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or get_llm_provider()

    def respond(self, payload: {{class_name}}PromptRequest) -> {{class_name}}PromptResponse:
        result = self.provider.generate_text(
            system_prompt=build_system_prompt(payload.topic),
            user_prompt=payload.prompt,
        )
        return {{class_name}}PromptResponse(
            response=result.text,
            provider=result.provider,
            model=result.model,
            topic=payload.topic,
        )
