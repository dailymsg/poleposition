from pole_position.cli.services.module_templates.renderer import render_template


def llm_integration_files(package_name: str) -> dict[str, str]:
    context = {"package_name": package_name}

    return {
        "integrations/__init__.py": render_template("llm/integrations_init.py.tpl", context),
        "integrations/llm/__init__.py": render_template("llm/__init__.py.tpl", context),
        "integrations/llm/schemas.py": render_template("llm/schemas.py.tpl", context),
        "integrations/llm/provider.py": render_template("llm/provider.py.tpl", context),
        "integrations/llm/factory.py": render_template("llm/factory.py.tpl", context),
        "integrations/llm/openai_client.py": render_template("llm/openai_client.py.tpl", context),
        "integrations/llm/anthropic_client.py": render_template(
            "llm/anthropic_client.py.tpl",
            context,
        ),
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
