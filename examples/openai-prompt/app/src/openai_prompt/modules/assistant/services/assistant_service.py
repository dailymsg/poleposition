from openai_prompt.bootstrap.logging import get_logger
from openai_prompt.modules.assistant.orchestrator import AssistantOrchestrator
from openai_prompt.modules.assistant.schemas import AssistantPromptRequest, AssistantPromptResponse


logger = get_logger(__name__)


class AssistantService:
    def __init__(self, orchestrator: AssistantOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or AssistantOrchestrator()

    def respond(self, payload: AssistantPromptRequest) -> AssistantPromptResponse:
        logger.info("Generating AI response", extra={"topic": payload.topic})
        return self.orchestrator.respond(payload)
