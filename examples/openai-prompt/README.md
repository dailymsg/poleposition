# OpenAI Prompt Scenario

This guide shows how to turn PolePosition's `ai-prompt` module template into a
working OpenAI-backed prompt endpoint.

The generated template is provider-agnostic on purpose. It creates the module
boundary, prompt builder, orchestrator, service, router, provider protocol, and
provider adapter files. You then install the SDK for the provider you want and
fill in the adapter.

For OpenAI, this tutorial uses the Responses API shape from the official
[OpenAI developer quickstart](https://platform.openai.com/docs/quickstart?api-mode=responses&lang=python)
and [Responses API reference](https://platform.openai.com/docs/api-reference/responses).

## Complete Runnable Source

This example includes a complete PolePosition-generated project:

```text
examples/openai-prompt/app/
```

Run it directly after setting `LLM_API_KEY`:

```bash
cd examples/openai-prompt/app
cp .env.example .env
uv sync --extra dev
uv run python -m openai_prompt.run
```

The rest of this guide explains how that `app/` project was built and why each
file exists.

## Scenario Goal

Build a prompt endpoint:

```text
POST /api/v1/assistant/respond
```

The client sends:

```json
{
  "topic": "support_reply",
  "prompt": "A customer says their invoice total looks wrong. Draft a reply."
}
```

The API sends a system prompt and user prompt to OpenAI, then returns:

```json
{
  "response": "...",
  "provider": "openai",
  "model": "gpt-5.4-mini",
  "topic": "support_reply"
}
```

## Step 1: Create the Project

This example does not need database wiring:

```bash
polepos start openai-prompt --db none
cd openai-prompt
cp .env.example .env
uv sync --extra dev
```

## Step 2: Generate the AI Prompt Module

```bash
polepos add module assistant --template ai-prompt
```

PolePosition creates:

```text
src/openai_prompt/modules/assistant/
  __init__.py
  orchestrator.py
  prompts.py
  router.py
  schemas.py
  services/
    __init__.py
    assistant_service.py
tests/integration/test_assistant.py
tests/unit/test_assistant_orchestrator.py
```

It also creates the shared provider boundary:

```text
src/openai_prompt/integrations/llm/
  __init__.py
  anthropic_client.py
  factory.py
  openai_client.py
  provider.py
  schemas.py
```

Why this structure matters:

- module files own the assistant use case
- `integrations/llm` owns provider-specific SDK code
- tests can patch the provider protocol without calling OpenAI
- switching providers later should not rewrite the FastAPI route

## Step 3: Install the OpenAI SDK

```bash
uv add openai
uv sync --extra dev
```

PolePosition does not install provider SDKs by default because the `ai-prompt`
template is provider-agnostic. Installing `openai` is the explicit opt-in for
this tutorial.

## Step 4: Configure `.env`

Use these values:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-5.4-mini
LLM_API_KEY=your_openai_api_key
LLM_BASE_URL=
LLM_TIMEOUT_SECONDS=30.0
LLM_TEMPERATURE=0.2
# LLM_MAX_TOKENS=
```

Why these values matter:

- `LLM_PROVIDER=openai` makes `get_llm_provider()` return `OpenAIProvider`
- `LLM_MODEL` selects the model used by the Responses API call
- `LLM_API_KEY` stays in local `.env`, not in source control
- `LLM_MAX_TOKENS` is optional; set it when you need a hard output limit

## Step 5: Review the Generated API Contract

The generated `src/openai_prompt/modules/assistant/schemas.py` already gives a
simple prompt contract:

```python
from pydantic import BaseModel, Field


class AssistantPromptRequest(BaseModel):
    prompt: str = Field(min_length=1)
    topic: str = Field(default="general", min_length=1, max_length=100)


class AssistantPromptResponse(BaseModel):
    response: str
    provider: str
    model: str
    topic: str
```

Why this file exists:

- request validation stays at the API edge
- `topic` lets the app choose a system prompt without exposing raw system
  instructions to clients
- the response includes provider/model so local tests and debugging can confirm
  which adapter handled the request

## Step 6: Shape the System Prompts

Replace `src/openai_prompt/modules/assistant/prompts.py`:

```python
def build_system_prompt(topic: str) -> str:
    normalized_topic = topic.strip().lower().replace("-", "_")

    if normalized_topic == "support_reply":
        return (
            "You write concise customer support replies. "
            "Acknowledge the issue, ask for any missing detail, and avoid "
            "promising refunds or account changes."
        )

    if normalized_topic == "product_explainer":
        return (
            "Explain the product idea in clear, practical language for a "
            "non-technical stakeholder."
        )

    if normalized_topic == "release_notes":
        return (
            "Write concise release notes. Group changes by user-facing impact "
            "and avoid internal implementation details."
        )

    return "Be clear, accurate, and concise while staying on topic."
```

Why this file exists:

- system prompts are application policy, not user input
- topic-specific prompts are easy to review in code
- the router stays small and does not contain prompt text

## Step 7: Implement the OpenAI Adapter

Replace `src/openai_prompt/integrations/llm/openai_client.py`:

```python
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from openai_prompt.integrations.llm.schemas import LLMTextResult


@dataclass(slots=True)
class OpenAIProvider:
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

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url or None,
            timeout=self.timeout_seconds,
        )
        request: dict[str, Any] = {
            "model": self.model,
            "instructions": system_prompt,
            "input": user_prompt,
            "temperature": self.temperature,
        }
        if self.max_tokens is not None:
            request["max_output_tokens"] = self.max_tokens

        response = client.responses.create(**request)
        return LLMTextResult(
            text=response.output_text,
            provider="openai",
            model=self.model,
        )
```

What this adapter does:

- it keeps OpenAI SDK imports out of the module route and service
- it uses `instructions` for the system prompt and `input` for the user's prompt
- it returns the generated `LLMTextResult` shape expected by the orchestrator
- it uses `response.output_text`, the convenience property exposed by the
  Responses API SDK examples

The rest of the generated flow can stay as-is:

- `factory.py` reads settings and constructs `OpenAIProvider`
- `orchestrator.py` combines `build_system_prompt()` with the user prompt
- `services/assistant_service.py` logs the workflow and delegates to the
  orchestrator
- `router.py` exposes `POST /respond`

## Step 8: Run the API

```bash
uv run python -m openai_prompt.run
```

Send a prompt:

```bash
curl -X POST http://localhost:8000/api/v1/assistant/respond \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "support_reply",
    "prompt": "A customer says their invoice total looks wrong. Draft a reply."
  }'
```

The response shape should be:

```json
{
  "response": "Hi ...",
  "provider": "openai",
  "model": "gpt-5.4-mini",
  "topic": "support_reply"
}
```

## Step 9: Test Without Calling OpenAI

Keep the generated unit test style: inject a provider stub into the
orchestrator. That tests prompt construction and response mapping without
network access or API cost.

The generated `tests/unit/test_assistant_orchestrator.py` already follows this
shape:

```python
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
```

Why this test is useful:

- it checks the module's prompt policy
- it proves provider output is mapped into the API response
- it does not require `LLM_API_KEY`
- it keeps live provider smoke tests separate from the default test suite

Run:

```bash
uv run pytest
polepos check
```

## Where Live Provider Tests Belong

Do not put live OpenAI calls in the default unit suite. If you need a smoke
test, keep it opt-in:

- require an environment variable such as `RUN_OPENAI_SMOKE=1`
- skip when `LLM_API_KEY` is missing
- send a tiny prompt
- assert only response shape, not exact prose

That keeps normal development deterministic and avoids accidental API spend.
