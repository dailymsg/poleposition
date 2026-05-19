from openai_prompt.integrations.llm.anthropic_client import AnthropicProvider
from openai_prompt.integrations.llm.openai_client import OpenAIProvider
from openai_prompt.integrations.llm.provider import LLMProvider
from openai_prompt.settings import get_settings


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
        f"Unsupported LLM provider '{settings.llm_provider}'. "
        "Expected one of: openai, anthropic."
    )
