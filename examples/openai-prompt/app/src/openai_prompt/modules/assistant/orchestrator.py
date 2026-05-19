from openai_prompt.integrations.llm.factory import get_llm_provider
from openai_prompt.integrations.llm.provider import LLMProvider
from openai_prompt.modules.assistant.prompts import build_system_prompt
from openai_prompt.modules.assistant.schemas import AssistantPromptRequest, AssistantPromptResponse


class AssistantOrchestrator:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or get_llm_provider()

    def respond(self, payload: AssistantPromptRequest) -> AssistantPromptResponse:
        result = self.provider.generate_text(
            system_prompt=build_system_prompt(payload.topic),
            user_prompt=payload.prompt,
        )
        return AssistantPromptResponse(
            response=result.text,
            provider=result.provider,
            model=result.model,
            topic=payload.topic,
        )
