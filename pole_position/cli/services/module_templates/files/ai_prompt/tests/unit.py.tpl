from {{package_name}}.integrations.llm.schemas import LLMTextResult
from {{package_name}}.modules.{{module_name}}.orchestrator import {{class_name}}Orchestrator
from {{package_name}}.modules.{{module_name}}.schemas import {{class_name}}PromptRequest


class StubProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def generate_text(self, *, system_prompt: str, user_prompt: str) -> LLMTextResult:
        self.calls.append((system_prompt, user_prompt))
        return LLMTextResult(
            text="Structured answer",
            provider="anthropic",
            model="claude-sonnet",
        )


def test_respond_builds_prompt_and_returns_provider_output() -> None:
    provider = StubProvider()
    orchestrator = {{class_name}}Orchestrator(provider=provider)

    result = orchestrator.respond(
        {{class_name}}PromptRequest(
            prompt="Summarize the release notes.",
            topic="release_notes",
        )
    )

    assert provider.calls == [
        (
            "Write concise release notes that highlight user-facing changes.",
            "Summarize the release notes.",
        )
    ]
    assert result.response == "Structured answer"
    assert result.provider == "anthropic"
    assert result.model == "claude-sonnet"
    assert result.topic == "release_notes"
