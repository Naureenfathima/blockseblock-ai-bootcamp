"""
Provider implementation that wraps an OpenAI-compatible chat completions endpoint.

Used for LLM_PROVIDER=openai. Can also target any other OpenAI-compatible host
(e.g. Azure OpenAI, Together AI) by setting OPENAI_BASE_URL in .env.
"""
import json

from openai import AsyncOpenAI

from shared.config import settings
from shared.providers.base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """Talks to any OpenAI-compatible /v1/chat/completions endpoint."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._api_key = api_key or settings.openai_api_key
        # base_url=None tells the openai library to use the default OpenAI endpoint.
        self._base_url = base_url or settings.openai_base_url or None
        self._model = model or settings.openai_model

    def _get_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
        )

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: list[dict] | None = None,
        response_format: dict | None = None,
    ) -> LLMResponse:
        """Send messages to the model and return a normalized response."""
        client = self._get_client()

        kwargs: dict = {}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if response_format:
            kwargs["response_format"] = response_format

        completion = await client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        message = completion.choices[0].message

        # Normalize tool_calls from the OpenAI shape to our common shape.
        normalized_tool_calls: list[dict] = []
        if message.tool_calls:
            for tc in message.tool_calls:
                normalized_tool_calls.append(
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        # arguments arrives as a JSON string — parse it to a dict
                        # so callers don't have to remember this quirk.
                        "arguments": json.loads(tc.function.arguments),
                    }
                )

        return LLMResponse(
            content=message.content,
            tool_calls=normalized_tool_calls,
            raw=completion.model_dump(),
            provider="openai",
            model=self._model,
        )

    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        """Transcribe audio to text using the provider's STT endpoint."""
        client = self._get_client()
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, audio_bytes),
        )
        return response.text

    async def synthesize_speech(self, text: str, voice: str = "default") -> bytes:
        """Convert text to speech using the provider's TTS endpoint."""
        client = self._get_client()
        # "alloy" is a neutral default voice; the caller can override.
        tts_voice = voice if voice != "default" else "alloy"
        response = await client.audio.speech.create(
            model="tts-1",
            voice=tts_voice,
            input=text,
        )
        return response.content
