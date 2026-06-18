"""
Factory that reads LLM_PROVIDER (and VOICE_PROVIDER) from config and returns
the correct provider instance.

Usage:
    from shared.providers.factory import get_provider

    provider = get_provider()           # LLM provider (chat/agents/RAG)
    voice    = get_provider("voice")    # Voice provider (STT/TTS, Feature 10)
"""
import functools

from shared.config import settings
from shared.providers.base import LLMProvider

_VALID_PROVIDERS = {
    "openai", "anthropic", "cohere", "ollama", "groq",
    "azure", "bedrock", "vertex", "custom",
}


def _build_provider(provider_name: str) -> LLMProvider:
    """Instantiate the provider class for the given provider name."""
    # Lazy imports so students who don't have a package installed (e.g. cohere)
    # don't hit an ImportError until they actually try to USE that provider.
    if provider_name == "openai":
        from shared.providers.openai_provider import OpenAIProvider

        _validate_fields(provider_name, ["openai_api_key"])
        return OpenAIProvider()

    if provider_name == "anthropic":
        from shared.providers.anthropic_provider import AnthropicProvider

        _validate_fields(provider_name, ["anthropic_api_key"])
        return AnthropicProvider()

    if provider_name == "cohere":
        from shared.providers.cohere_provider import CohereProvider

        _validate_fields(provider_name, ["cohere_api_key"])
        return CohereProvider()

    if provider_name == "ollama":
        from shared.providers.ollama_provider import OllamaProvider

        # Ollama needs no API key — but we still run the connectivity check at
        # startup so students get a clear error if `ollama serve` isn't running.
        return OllamaProvider()

    if provider_name == "groq":
        from shared.providers.groq_provider import GroqProvider

        _validate_fields(provider_name, ["groq_api_key"])
        return GroqProvider()

    if provider_name == "azure":
        from shared.providers.azure_provider import AzureProvider

        _validate_fields(
            provider_name,
            ["azure_openai_api_key", "azure_openai_endpoint", "azure_openai_deployment_name"],
        )
        return AzureProvider()

    if provider_name == "bedrock":
        from shared.providers.bedrock_provider import BedrockProvider

        _validate_fields(provider_name, ["aws_access_key_id", "aws_secret_access_key", "bedrock_model_id"])
        return BedrockProvider()

    if provider_name == "vertex":
        from shared.providers.vertex_provider import VertexProvider

        _validate_fields(provider_name, ["gcp_project_id", "vertex_model"])
        return VertexProvider()

    if provider_name == "custom":
        from shared.providers.openai_provider import OpenAIProvider

        _validate_fields(provider_name, ["custom_base_url", "custom_model"])
        return OpenAIProvider(
            api_key=settings.custom_api_key or "custom",
            base_url=settings.custom_base_url,
            model=settings.custom_model,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER value: '{provider_name}'. "
        f"Valid options are: {', '.join(sorted(_VALID_PROVIDERS))}. "
        f"Check your .env file."
    )


def _validate_fields(provider: str, required_settings: list[str]) -> None:
    """Raise a clear error if a required .env variable is missing for the chosen provider."""
    missing = [
        field for field in required_settings if not getattr(settings, field, "")
    ]
    if missing:
        env_var_names = [f.upper() for f in missing]
        raise ValueError(
            f"LLM_PROVIDER={provider!r} but the following required .env variable(s) "
            f"are not set: {', '.join(env_var_names)}. "
            f"See docs/provider-setup-guide.md for instructions."
        )


@functools.lru_cache(maxsize=4)
def get_provider(role: str = "llm") -> LLMProvider:
    """
    Return the provider instance for the given role.

    Args:
        role: "llm" (default) for chat/agents/RAG, or "voice" for STT/TTS.
              The "voice" role uses VOICE_PROVIDER if set, otherwise falls back
              to LLM_PROVIDER — so students who use a speech-capable provider
              everywhere don't need to set VOICE_PROVIDER separately.

    The result is cached — provider construction (which may create HTTP clients)
    only happens once per process, regardless of how many times this is called.
    """
    if role == "voice":
        provider_name = settings.effective_voice_provider().lower().strip()
    else:
        provider_name = settings.llm_provider.lower().strip()

    if not provider_name or provider_name not in _VALID_PROVIDERS:
        raise ValueError(
            f"LLM_PROVIDER is set to '{provider_name}', which is not valid. "
            f"Choose one of: {', '.join(sorted(_VALID_PROVIDERS))}. "
            f"Edit your .env file to fix this."
        )

    return _build_provider(provider_name)
