from dataclasses import dataclass


SUPPORTED_MODULE_TEMPLATES = ("standard", "ai-prompt")


@dataclass(frozen=True)
class ModuleTemplate:
    files: dict[str, str]
    integration_test_name: str
    integration_test_content: str
    unit_test_name: str
    unit_test_content: str
    update_db_models: bool = True
    ensure_llm_integrations: bool = False
    ensure_llm_settings: bool = False


def build_module_template(
    *,
    template: str,
    package_name: str,
    module_name: str,
) -> ModuleTemplate:
    class_name = _to_class_name(module_name)

    if template == "standard":
        return ModuleTemplate(
            files={
                "__init__.py": _standard_module_init_content(),
                "model.py": _standard_model_content(package_name, module_name, class_name),
                "repository.py": _standard_repository_content(
                    package_name, module_name, class_name
                ),
                "schemas.py": _standard_schemas_content(class_name),
                "service.py": _standard_service_content(package_name, module_name, class_name),
                "router.py": _standard_router_content(package_name, module_name, class_name),
            },
            integration_test_name=f"test_{module_name}.py",
            integration_test_content=_standard_integration_test_content(module_name, class_name),
            unit_test_name=f"test_{module_name}_service.py",
            unit_test_content=_standard_unit_test_content(package_name, module_name, class_name),
        )

    if template == "ai-prompt":
        return ModuleTemplate(
            files={
                "__init__.py": _ai_module_init_content(),
                "schemas.py": _ai_schemas_content(class_name),
                "prompts.py": _ai_prompts_content(),
                "orchestrator.py": _ai_orchestrator_content(package_name, module_name, class_name),
                "service.py": _ai_service_content(package_name, module_name, class_name),
                "router.py": _ai_router_content(package_name, module_name, class_name),
            },
            integration_test_name=f"test_{module_name}.py",
            integration_test_content=_ai_integration_test_content(package_name, module_name, class_name),
            unit_test_name=f"test_{module_name}_orchestrator.py",
            unit_test_content=_ai_unit_test_content(package_name, module_name, class_name),
            update_db_models=False,
            ensure_llm_integrations=True,
            ensure_llm_settings=True,
        )

    supported = ", ".join(SUPPORTED_MODULE_TEMPLATES)
    raise ValueError(
        f"Unsupported module template '{template}'. Expected one of: {supported}."
    )


def llm_integration_files(package_name: str) -> dict[str, str]:
    return {
        "integrations/__init__.py": _integrations_init_content(),
        "integrations/llm/__init__.py": _llm_init_content(),
        "integrations/llm/schemas.py": _llm_schemas_content(),
        "integrations/llm/provider.py": _llm_provider_content(package_name),
        "integrations/llm/factory.py": _llm_factory_content(package_name),
        "integrations/llm/openai_client.py": _openai_client_content(package_name),
        "integrations/llm/anthropic_client.py": _anthropic_client_content(package_name),
    }


def llm_settings_block() -> list[str]:
    return [
        '    llm_provider: str = "openai"',
        '    llm_model: str = "gpt-5.4-mini"',
        '    llm_api_key: str = ""',
        '    llm_base_url: str = ""',
        "    llm_timeout_seconds: float = 30.0",
        "    llm_temperature: float = 0.2",
        "    llm_max_tokens: int | None = None",
    ]


def llm_env_block() -> list[str]:
    return [
        "LLM_PROVIDER=openai",
        "LLM_MODEL=gpt-5.4-mini",
        "LLM_API_KEY=",
        "LLM_BASE_URL=",
        "LLM_TIMEOUT_SECONDS=30.0",
        "LLM_TEMPERATURE=0.2",
        "# LLM_MAX_TOKENS=",
    ]


def _standard_module_init_content() -> str:
    return '''__all__ = [
    "model",
    "repository",
    "router",
    "schemas",
    "service",
]
'''


def _standard_model_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from {package_name}.db.base import Base


class {class_name}(Base):
    __tablename__ = "{module_name}"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
'''


def _standard_repository_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from sqlalchemy import select
from sqlalchemy.orm import Session

from {package_name}.modules.{module_name}.model import {class_name}


class {class_name}Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[{class_name}]:
        statement = select({class_name}).order_by({class_name}.id.asc())
        return list(self.db.scalars(statement))

    def create(self, *, name: str) -> {class_name}:
        item = {class_name}(name=name)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
'''


def _standard_schemas_content(class_name: str) -> str:
    return f'''from pydantic import BaseModel, ConfigDict, Field


class {class_name}Create(BaseModel):
    name: str = Field(min_length=3, max_length=120)


class {class_name}Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
'''


def _standard_service_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from sqlalchemy.orm import Session

from {package_name}.bootstrap.logging import get_logger
from {package_name}.modules.{module_name}.model import {class_name}
from {package_name}.modules.{module_name}.repository import {class_name}Repository
from {package_name}.modules.{module_name}.schemas import {class_name}Create


logger = get_logger(__name__)


class {class_name}Service:
    def __init__(self, db: Session) -> None:
        self.repository = {class_name}Repository(db)

    def list_{module_name}(self) -> list[{class_name}]:
        logger.info("Listing {module_name}")
        return self.repository.list()

    def create_{module_name}(self, payload: {class_name}Create) -> {class_name}:
        logger.info("Creating {module_name}", extra={{"name": payload.name}})
        return self.repository.create(name=payload.name)
'''


def _standard_router_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from {package_name}.api.deps import db_session
from {package_name}.modules.{module_name}.schemas import {class_name}Create, {class_name}Read
from {package_name}.modules.{module_name}.service import {class_name}Service


router = APIRouter()


@router.get("/", response_model=list[{class_name}Read])
def list_{module_name}(db: Session = Depends(db_session)) -> list[{class_name}Read]:
    return {class_name}Service(db).list_{module_name}()


@router.post("/", response_model={class_name}Read, status_code=status.HTTP_201_CREATED)
def create_{module_name}(payload: {class_name}Create, db: Session = Depends(db_session)) -> {class_name}Read:
    return {class_name}Service(db).create_{module_name}(payload)
'''


def _standard_integration_test_content(module_name: str, class_name: str) -> str:
    return f'''from fastapi.testclient import TestClient


def test_create_and_list_{module_name}(client: TestClient) -> None:
    create_response = client.post("/api/v1/{module_name}/", json={{"name": "Main {class_name}"}})
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/{module_name}/")
    assert list_response.status_code == 200

    payload = list_response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Main {class_name}"
'''


def _standard_unit_test_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from unittest.mock import Mock

from {package_name}.modules.{module_name}.service import {class_name}Service


def test_list_{module_name}_delegates_to_repository() -> None:
    service = {class_name}Service(db=Mock())
    service.repository = Mock()

    service.list_{module_name}()

    service.repository.list.assert_called_once_with()
'''


def _ai_module_init_content() -> str:
    return '''__all__ = [
    "orchestrator",
    "prompts",
    "router",
    "schemas",
    "service",
]
'''


def _ai_schemas_content(class_name: str) -> str:
    return f'''from pydantic import BaseModel, Field


class {class_name}PromptRequest(BaseModel):
    prompt: str = Field(min_length=1)
    topic: str = Field(default="general", min_length=1, max_length=100)


class {class_name}PromptResponse(BaseModel):
    response: str
    provider: str
    model: str
    topic: str
'''


def _ai_prompts_content() -> str:
    return '''def build_system_prompt(topic: str) -> str:
    normalized_topic = topic.strip().lower().replace("-", "_")

    if normalized_topic == "product_explainer":
        return "Explain the topic in clear, non-technical language."

    if normalized_topic == "support_reply":
        return "Draft a concise, professional customer support response."

    if normalized_topic == "release_notes":
        return "Write concise release notes that highlight user-facing changes."

    return "Be clear, accurate, and concise while staying on topic."
'''


def _ai_orchestrator_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from {package_name}.integrations.llm.factory import get_llm_provider
from {package_name}.integrations.llm.provider import LLMProvider
from {package_name}.modules.{module_name}.prompts import build_system_prompt
from {package_name}.modules.{module_name}.schemas import {class_name}PromptRequest, {class_name}PromptResponse


class {class_name}Orchestrator:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or get_llm_provider()

    def respond(self, payload: {class_name}PromptRequest) -> {class_name}PromptResponse:
        result = self.provider.generate_text(
            system_prompt=build_system_prompt(payload.topic),
            user_prompt=payload.prompt,
        )
        return {class_name}PromptResponse(
            response=result.text,
            provider=result.provider,
            model=result.model,
            topic=payload.topic,
        )
'''


def _ai_service_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from {package_name}.bootstrap.logging import get_logger
from {package_name}.modules.{module_name}.orchestrator import {class_name}Orchestrator
from {package_name}.modules.{module_name}.schemas import {class_name}PromptRequest, {class_name}PromptResponse


logger = get_logger(__name__)


class {class_name}Service:
    def __init__(self, orchestrator: {class_name}Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or {class_name}Orchestrator()

    def respond(self, payload: {class_name}PromptRequest) -> {class_name}PromptResponse:
        logger.info("Generating AI response", extra={{"topic": payload.topic}})
        return self.orchestrator.respond(payload)
'''


def _ai_router_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from fastapi import APIRouter

from {package_name}.modules.{module_name}.schemas import {class_name}PromptRequest, {class_name}PromptResponse
from {package_name}.modules.{module_name}.service import {class_name}Service


router = APIRouter()


@router.post("/respond", response_model={class_name}PromptResponse)
def respond(payload: {class_name}PromptRequest) -> {class_name}PromptResponse:
    return {class_name}Service().respond(payload)
'''


def _ai_integration_test_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from unittest.mock import patch

from fastapi.testclient import TestClient

from {package_name}.integrations.llm.schemas import LLMTextResult


class StubProvider:
    def generate_text(self, *, system_prompt: str, user_prompt: str) -> LLMTextResult:
        assert system_prompt
        assert user_prompt == "Explain PolePosition simply."
        return LLMTextResult(
            text="PolePosition helps teams start FastAPI projects faster.",
            provider="openai",
            model="gpt-5.4-mini",
        )


def test_respond_{module_name}(client: TestClient) -> None:
    with patch(
        "{package_name}.modules.{module_name}.orchestrator.get_llm_provider",
        return_value=StubProvider(),
    ):
        response = client.post(
            "/api/v1/{module_name}/respond",
            json={{"prompt": "Explain PolePosition simply.", "topic": "product_explainer"}},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["response"] == "PolePosition helps teams start FastAPI projects faster."
    assert payload["provider"] == "openai"
    assert payload["topic"] == "product_explainer"
'''


def _ai_unit_test_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from {package_name}.integrations.llm.schemas import LLMTextResult
from {package_name}.modules.{module_name}.orchestrator import {class_name}Orchestrator
from {package_name}.modules.{module_name}.schemas import {class_name}PromptRequest


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
    orchestrator = {class_name}Orchestrator(provider=provider)

    result = orchestrator.respond(
        {class_name}PromptRequest(
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
'''


def _integrations_init_content() -> str:
    return '''__all__ = [
    "llm",
]
'''


def _llm_init_content() -> str:
    return '''from __future__ import annotations

from .factory import get_llm_provider


__all__ = [
    "get_llm_provider",
]
'''


def _llm_schemas_content() -> str:
    return '''from pydantic import BaseModel


class LLMTextResult(BaseModel):
    text: str
    provider: str
    model: str
'''


def _llm_provider_content(package_name: str) -> str:
    return f'''from typing import Protocol

from {package_name}.integrations.llm.schemas import LLMTextResult


class LLMProvider(Protocol):
    def generate_text(self, *, system_prompt: str, user_prompt: str) -> LLMTextResult:
        ...
'''


def _llm_factory_content(package_name: str) -> str:
    return f'''from {package_name}.integrations.llm.anthropic_client import AnthropicProvider
from {package_name}.integrations.llm.openai_client import OpenAIProvider
from {package_name}.integrations.llm.provider import LLMProvider
from {package_name}.settings import get_settings


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    provider_name = settings.llm_provider.strip().lower()

    if provider_name == "openai":
        return OpenAIProvider(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url or None,
            timeout_seconds=settings.llm_timeout_seconds,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    if provider_name == "anthropic":
        return AnthropicProvider(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url or None,
            timeout_seconds=settings.llm_timeout_seconds,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    raise ValueError(
        f"Unsupported LLM provider '{{settings.llm_provider}}'. "
        "Expected one of: openai, anthropic."
    )
'''


def _openai_client_content(package_name: str) -> str:
    return f'''from dataclasses import dataclass

from {package_name}.integrations.llm.schemas import LLMTextResult


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

        raise NotImplementedError(
            "Install an OpenAI-compatible SDK or implement the adapter in "
            f"{{__file__}} for your preferred provider workflow."
        )
'''


def _anthropic_client_content(package_name: str) -> str:
    return f'''from dataclasses import dataclass

from {package_name}.integrations.llm.schemas import LLMTextResult


@dataclass(slots=True)
class AnthropicProvider:
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

        raise NotImplementedError(
            "Install an Anthropic-compatible SDK or implement the adapter in "
            f"{{__file__}} for your preferred provider workflow."
        )
'''


def _to_class_name(module_name: str) -> str:
    return "".join(part.capitalize() for part in module_name.split("_"))
