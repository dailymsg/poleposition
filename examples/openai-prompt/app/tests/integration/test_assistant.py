from unittest.mock import patch

from fastapi.testclient import TestClient

from openai_prompt.integrations.llm.schemas import LLMTextResult


class StubProvider:
    def generate_text(self, *, system_prompt: str, user_prompt: str) -> LLMTextResult:
        assert system_prompt
        assert user_prompt == "Explain PolePosition simply."
        return LLMTextResult(
            text="PolePosition helps teams start FastAPI projects faster.",
            provider="openai",
            model="gpt-5.4-mini",
        )


def test_respond_assistant(client: TestClient) -> None:
    with patch(
        "openai_prompt.modules.assistant.orchestrator.get_llm_provider",
        return_value=StubProvider(),
    ):
        response = client.post(
            "/api/v1/assistant/respond",
            json={"prompt": "Explain PolePosition simply.", "topic": "product_explainer"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["response"] == "PolePosition helps teams start FastAPI projects faster."
    assert payload["provider"] == "openai"
    assert payload["topic"] == "product_explainer"
