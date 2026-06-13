"""
Provider implementation for locally-running models via Ollama.

Ollama exposes an OpenAI-compatible endpoint at {OLLAMA_BASE_URL}/v1, so this
provider reuses OpenAIProvider's logic by pointing it at the local server.
No API key is needed — Ollama runs entirely on the student's own machine.

To use this provider:
  1. Install Ollama from https://ollama.com
  2. Run: ollama pull llama3.1  (or whichever model you prefer)
  3. Run: ollama serve
  4. Set LLM_PROVIDER=ollama in .env

IMPORTANT: Many local models do not reliably support tool calling or JSON mode.
  - Tool calling (Features 7-9): works well with llama3.1, mistral-nemo, qwen2.5
  - For voice (Feature 10): set VOICE_PROVIDER=openai — Ollama doesn't do speech
"""
import logging

from shared.config import settings
from shared.providers.base import LLMProvider, LLMResponse
from shared.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

# Models known to support tool calling via Ollama's native function calling.
# This list is informational — we warn, not crash, when an unknown model is used.
_TOOL_CAPABLE_MODELS = {
    "llama3.1",
    "llama3.2",
    "mistral-nemo",
    "qwen2.5",
    "qwen2.5-coder",
    "firefunction-v2",
}


class OllamaProvider(OpenAIProvider):
    """
    Runs local models via Ollama's OpenAI-compatible endpoint.

    Inherits all request/response logic from OpenAIProvider — the only
    difference is the base_url (points at the local Ollama server) and the
    model name (whatever the student has pulled locally).
    """

    def __init__(self) -> None:
        # "ollama" is a dummy key — Ollama ignores the auth header but the openai
        # library requires a non-empty api_key parameter.
        super().__init__(
            api_key="ollama",
            base_url=f"{settings.ollama_base_url}/v1",
            model=settings.ollama_model,
        )
        self._provider_name = "ollama"

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: list[dict] | None = None,
        response_format: dict | None = None,
    ) -> LLMResponse:
        """Send messages to a locally running model via Ollama.

        Falls back to plain chat (ignoring tools / response_format) when the
        active model is not known to support those features, rather than crashing
        with a cryptic error.
        """
        model_base = self._model.split(":")[0].lower()

        if tools and model_base not in _TOOL_CAPABLE_MODELS:
            logger.warning(
                "Model '%s' may not support tool calling reliably. "
                "Falling back to plain chat (tools ignored). "
                "Switch to a tool-capable model (e.g. llama3.1, qwen2.5) for "
                "Features 7-9. See docs/provider-setup-guide.md.",
                self._model,
            )
            tools = None

        if response_format and model_base not in _TOOL_CAPABLE_MODELS:
            logger.warning(
                "Model '%s' may not support JSON mode reliably. "
                "Falling back to plain chat (response_format ignored). "
                "If you need structured output locally, use llama3.1 or qwen2.5.",
                self._model,
            )
            response_format = None

        result = await super().chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            response_format=response_format,
        )
        result.provider = "ollama"
        return result

    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        raise NotImplementedError(
            "Local Ollama models don't include speech APIs in this course setup. "
            "Set VOICE_PROVIDER=openai in .env to enable voice (Feature 10) while "
            "keeping LLM_PROVIDER=ollama for chat. "
            "See docs/provider-setup-guide.md for details."
        )

    async def synthesize_speech(self, text: str, voice: str = "default") -> bytes:
        raise NotImplementedError(
            "Local Ollama models don't include speech APIs in this course setup. "
            "Set VOICE_PROVIDER=openai in .env to enable voice (Feature 10) while "
            "keeping LLM_PROVIDER=ollama for chat. "
            "See docs/provider-setup-guide.md for details."
        )
