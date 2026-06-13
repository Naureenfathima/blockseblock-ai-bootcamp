"""
Abstract base class that every LLM provider must implement.

This contract ensures that application code (chat endpoints, agents, RAG) can
call any provider through the same interface — switching providers is a .env
change, not a code change.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    """
    Normalized response returned by every provider's chat() method.

    Application code reads .content and .tool_calls regardless of which
    provider produced the response. The .raw field is available for debugging
    when you need to inspect the provider's original payload.
    """

    content: str | None
    """The text response from the model, or None if the model only made tool calls."""

    tool_calls: list[dict] = field(default_factory=list)
    """
    Normalized tool calls in the format:
      [{"id": "call_abc", "name": "function_name", "arguments": {"key": "value"}}]
    Empty list when the model produced plain text with no tool invocations.
    """

    raw: dict = field(default_factory=dict)
    """The original provider response as a dict, for debugging."""

    provider: str = ""
    """Which provider generated this response (e.g. "openai", "anthropic")."""

    model: str = ""
    """Which model was used (e.g. "gpt-4o-mini", "claude-sonnet-4-6")."""


class LLMProvider(ABC):
    """
    Abstract interface that every LLM provider class must implement.

    Students never interact with this class directly — they call functions in
    shared/llm_client.py, which delegates to whichever provider is active.
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: list[dict] | None = None,
        response_format: dict | None = None,
    ) -> LLMResponse:
        """
        Send a list of messages to the model and return the response.

        Args:
            messages: Conversation history as OpenAI-style message dicts:
                      [{"role": "system"|"user"|"assistant", "content": "..."}]
            temperature: 0 = focused/deterministic, 1 = creative/varied.
            max_tokens: Hard cap on response length.
            tools: OpenAI-style tool schemas for function/tool calling. None
                   means no tools are available.
            response_format: OpenAI-style format hint, e.g.
                             {"type": "json_object"} to request JSON output.

        Returns:
            A normalized LLMResponse with .content and .tool_calls populated.
        """

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        """
        Convert audio to text (Speech-to-Text).

        Args:
            audio_bytes: Raw audio file bytes (e.g. WAV, MP3, WebM).
            filename: Original filename including extension — used to infer format.

        Returns:
            The transcribed text as a plain string.

        Raises:
            NotImplementedError: If this provider does not support STT.
        """

    @abstractmethod
    async def synthesize_speech(self, text: str, voice: str = "default") -> bytes:
        """
        Convert text to spoken audio (Text-to-Speech).

        Args:
            text: The text to speak aloud.
            voice: Provider-specific voice name or "default".

        Returns:
            Raw audio bytes (typically MP3).

        Raises:
            NotImplementedError: If this provider does not support TTS.
        """
