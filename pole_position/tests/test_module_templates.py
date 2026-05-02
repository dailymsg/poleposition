import pytest

from pole_position.cli.services.module_templates import (
    SUPPORTED_MODULE_TEMPLATES,
    build_module_template,
    llm_env_block,
    llm_integration_files,
    llm_settings_block,
)
from pole_position.cli.services.module_templates.naming import to_class_name
from pole_position.cli.services.module_templates.renderer import render_template


def test_supported_module_templates_are_stable() -> None:
    assert SUPPORTED_MODULE_TEMPLATES == ("standard", "ai-prompt")


def test_to_class_name_normalizes_module_names() -> None:
    assert to_class_name("garage") == "Garage"
    assert to_class_name("race_results") == "RaceResults"


def test_render_template_replaces_context_values() -> None:
    rendered = render_template(
        "standard/model.py.tpl",
        {
            "package_name": "shop_api",
            "module_name": "customers",
            "class_name": "Customers",
        },
    )

    assert "from shop_api.db.base import Base" in rendered
    assert "class Customers(Base):" in rendered
    assert '__tablename__ = "customers"' in rendered
    assert "{{" not in rendered
    assert "}}" not in rendered


def test_standard_template_contract() -> None:
    template = build_module_template(
        template="standard",
        package_name="shop_api",
        module_name="customers",
    )

    assert set(template.files) == {
        "__init__.py",
        "model.py",
        "repository.py",
        "router.py",
        "schemas.py",
        "service.py",
    }
    assert template.integration_test_name == "test_customers.py"
    assert template.unit_test_name == "test_customers_service.py"
    assert template.update_db_models is True
    assert template.ensure_llm_integrations is False
    assert template.ensure_llm_settings is False
    assert "from shop_api.bootstrap.logging import get_logger" in template.files["service.py"]
    assert 'client.post("/api/v1/customers/"' in template.integration_test_content


def test_ai_prompt_template_contract() -> None:
    template = build_module_template(
        template="ai-prompt",
        package_name="shop_api",
        module_name="assistant",
    )

    assert set(template.files) == {
        "__init__.py",
        "orchestrator.py",
        "prompts.py",
        "router.py",
        "schemas.py",
        "service.py",
    }
    assert template.integration_test_name == "test_assistant.py"
    assert template.unit_test_name == "test_assistant_orchestrator.py"
    assert template.update_db_models is False
    assert template.ensure_llm_integrations is True
    assert template.ensure_llm_settings is True
    assert "get_llm_provider" in template.files["orchestrator.py"]
    assert '"/api/v1/assistant/respond"' in template.integration_test_content


def test_unknown_module_template_raises_clear_error() -> None:
    with pytest.raises(ValueError) as exc_info:
        build_module_template(
            template="unknown",
            package_name="shop_api",
            module_name="assistant",
        )

    assert "Unsupported module template 'unknown'" in str(exc_info.value)
    assert "standard, ai-prompt" in str(exc_info.value)


def test_llm_integration_files_contract() -> None:
    files = llm_integration_files("shop_api")

    assert set(files) == {
        "integrations/__init__.py",
        "integrations/llm/__init__.py",
        "integrations/llm/anthropic_client.py",
        "integrations/llm/factory.py",
        "integrations/llm/openai_client.py",
        "integrations/llm/provider.py",
        "integrations/llm/schemas.py",
    }
    assert "from shop_api.settings import get_settings" in files["integrations/llm/factory.py"]
    assert "{{" not in "\n".join(files.values())
    assert "}}" not in "\n".join(files.values())


def test_llm_settings_and_env_blocks() -> None:
    settings_block = llm_settings_block()
    env_block = llm_env_block()

    assert '    llm_provider: str = "openai"' in settings_block
    assert "    llm_max_tokens: int | None = None" in settings_block
    assert "LLM_PROVIDER=openai" in env_block
    assert "# LLM_MAX_TOKENS=" in env_block
