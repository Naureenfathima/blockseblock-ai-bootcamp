"""
Public interface for all LLM calls in the AI Engineering Bootcamp.

Every feature imports from here. The underlying provider is configured entirely
through .env — switching providers never requires changing feature code.

Quick reference:
    from shared.llm_client import call_llm, transcribe_audio, synthesize_speech
    from shared.providers.base import LLMResponse
"""
from shared.providers.base import LLMResponse
from shared.providers.factory import get_provider


async def call_llm(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1000,
    tools: list[dict] | None = None,
    response_format: dict | None = None,
    **kwargs,
) -> LLMResponse:
    """
    Send a conversation to the configured LLM and return the response.

    Args:
        messages: Conversation history as a list of message dicts in the
                  OpenAI style: [{"role": "system"|"user"|"assistant", "content": "..."}].
                  Every provider's implementation translates this into its own
                  native format internally.
        temperature: Controls randomness. 0 = predictable, 1 = creative.
        max_tokens: Maximum response length in tokens (~¾ of a word each).
        tools: OpenAI-style tool schemas if the model should be able to call
               functions. None means plain chat with no tools.
        response_format: OpenAI-style hint for structured output, e.g.
                         {"type": "json_object"} to request JSON.
        **kwargs: Reserved for future use; currently ignored.

    Returns:
        LLMResponse with:
          .content     — the model's text reply (str or None if only tools called)
          .tool_calls  — list of {"id", "name", "arguments"} dicts (empty if none)
          .provider    — which provider answered ("openai", "anthropic", etc.)
          .model       — which model was used
          .raw         — the original provider response dict, for debugging
    """
    provider = get_provider("llm")
    return await provider.chat(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        tools=tools,
        response_format=response_format,
    )


async def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    """
    Convert spoken audio to text (Speech-to-Text).

    Uses the VOICE_PROVIDER if set in .env, otherwise the main LLM_PROVIDER.
    This lets students run chat on a provider that doesn't support speech while
    still using a speech-capable provider for Feature 10.

    Args:
        audio_bytes: Raw audio file bytes (WAV, MP3, WebM, etc.).
        filename: The original filename including extension (used to detect format).

    Returns:
        The transcribed text as a plain string.
    """
    provider = get_provider("voice")
    return await provider.transcribe(audio_bytes, filename)


async def synthesize_speech(text: str, voice: str = "default") -> bytes:
    """
    Convert text to spoken audio (Text-to-Speech).

    Uses the VOICE_PROVIDER if set in .env, otherwise the main LLM_PROVIDER.

    Args:
        text: The text to speak aloud.
        voice: Provider-specific voice name. Use "default" for the provider's
               default voice.

    Returns:
        Raw audio bytes (typically MP3), ready to send to the browser.
    """
    provider = get_provider("voice")
    return await provider.synthesize_speech(text, voice)
