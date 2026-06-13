"""
Startup validation for the configured LLM provider.

Call check_provider_config() once when the FastAPI app starts to surface
configuration problems immediately — before the first chat message hits a
cryptic 500 error.
"""
import asyncio
import logging

import httpx

from shared.config import settings
from shared.providers.factory import get_provider

logger = logging.getLogger(__name__)


async def check_provider_config() -> None:
    """
    Validate the active provider's configuration and connectivity.

    Raises a RuntimeError with a plain-English message if anything critical is
    missing or unreachable. This is intentionally loud — students should see the
    error the moment they start the server, not when they send their first message.
    """
    provider_name = settings.llm_provider.lower().strip()

    # Attempt to build the provider — this validates required env vars.
    try:
        get_provider("llm")
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

    # For Ollama, also check that the local server is actually running.
    if provider_name == "ollama":
        await _check_ollama_reachable(settings.ollama_base_url)

    # If a separate voice provider is configured, validate it too.
    voice_name = settings.effective_voice_provider().lower().strip()
    if voice_name != provider_name:
        try:
            get_provider("voice")
        except ValueError as exc:
            raise RuntimeError(
                f"VOICE_PROVIDER is configured but has a problem: {exc}"
            ) from exc
        if voice_name == "ollama":
            await _check_ollama_reachable(settings.ollama_base_url)

    logger.info("Provider check passed: LLM=%s, Voice=%s", provider_name, voice_name)


async def _check_ollama_reachable(base_url: str) -> None:
    """Ping the Ollama server; raise a clear error if it's not responding."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(base_url)
            response.raise_for_status()
    except Exception:
        raise RuntimeError(
            f"Can't reach Ollama at {base_url} — is `ollama serve` running? "
            f"Start Ollama, then restart the server. "
            f"If you installed Ollama but haven't started it, run `ollama serve` "
            f"in a separate terminal window."
        )
