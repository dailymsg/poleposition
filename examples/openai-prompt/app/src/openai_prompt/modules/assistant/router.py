from fastapi import APIRouter

from openai_prompt.modules.assistant.schemas import AssistantPromptRequest, AssistantPromptResponse
from openai_prompt.modules.assistant.services import AssistantService


router = APIRouter()


@router.post("/respond", response_model=AssistantPromptResponse)
def respond(payload: AssistantPromptRequest) -> AssistantPromptResponse:
    return AssistantService().respond(payload)
