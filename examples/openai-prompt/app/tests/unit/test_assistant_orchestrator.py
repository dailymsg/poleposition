from openai_prompt.integrations.llm.schemas import LLMTextResult
from openai_prompt.modules.assistant.orchestrator import AssistantOrchestrator
from openai_prompt.modules.assistant.schemas import AssistantPromptRequest


class StubProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def generate_text(self, *, system_prompt: str, user_prompt: str) -> LLMTextResult:
        self.calls.append((system_prompt, user_prompt))
        return LLMTextResult(
            text="Structured answer",
            provider="openai",
            model="test-model",
        )


def test_respond_builds_prompt_and_returns_provider_output() -> None:
    provider = StubProvider()
    orchestrator = AssistantOrchestrator(provider=provider)

    result = orchestrator.respond(
        AssistantPromptRequest(
            prompt="Draft a reply.",
            topic="support_reply",
        )
    )

    assert provider.calls == [
        (
            "You write concise customer support replies. "
            "Acknowledge the issue, ask for any missing detail, and avoid "
            "promising refunds or account changes.",
            "Draft a reply.",
        )
    ]
    assert result.response == "Structured answer"
    assert result.provider == "openai"
    assert result.model == "test-model"
    assert result.topic == "support_reply"
