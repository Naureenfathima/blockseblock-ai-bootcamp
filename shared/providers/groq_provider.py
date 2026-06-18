"""
Provider implementation for Groq — an inference company (not a model company)
that runs open-weight models (Llama, Mixtral, Gemma) on custom LPU hardware
for very fast, low-cost inference.

WHY GROQ FOR THIS COURSE:
  Groq's LPU (Language Processing Unit) delivers dramatically faster inference
  than GPU-based cloud providers — often 10-20x faster at competitive pricing,
  with a generous free tier (no credit card required). This makes it ideal for:
    - Feature 10 voice pipeline: lower latency = more natural voice conversation
    - Features 7-9 agents: each planning step is a separate LLM call — speed matters
    - Eval harness: running 10+ eval cases needs to be fast to be practical
  Groq's API is fully OpenAI-compatible, so this provider needs almost no
  translation layer — tool calling, JSON mode, and streaming all work identically.

RECOMMENDED GROQ MODELS:
  - llama-3.3-70b-versatile  → best quality + strong tool calling (Features 7-9)
  - llama-3.1-8b-instant     → fastest + cheapest, ideal for chat/RAG (Features 1-6)
                                and voice pipeline (Feature 10)
  - mixtral-8x7b-32768       → 32K context window, best for long documents and
                                extended conversation history (Feature 3 long sessions)
  - gemma2-9b-it             → Google's Gemma 2, well-rounded, good structured output
  - whisper-large-v3         → STT model for Feature 10 voice transcription

Get a free API key at: console.groq.com (no credit card required)

To use this provider, set in .env:
  LLM_PROVIDER=groq
  GROQ_API_KEY=your_key_here
  GROQ_MODEL=llama-3.3-70b-versatile   # or any model above
"""
from typing import Optional, List

import openai

from shared.config import settings
from shared.providers.base import LLMProvider, LLMResponse
from shared.providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """
    Runs inference on Groq's LPU hardware via their OpenAI-compatible API.

    Inherits all request/response logic from OpenAIProvider — the only
    differences are the base_url (api.groq.com) and the model name. Tool
    calling, JSON mode, structured output, and streaming all work identically
    to OpenAI — no translation layer needed.
    """

    def __init__(self) -> None:
        super().__init__(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            model=settings.groq_model,
        )
        self._provider_name = "groq"

    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        """
        Transcribe audio using Groq's Whisper endpoint.

        Groq hosts Whisper-large-v3 and offers one of the fastest and most
        accurate transcription APIs available, included in the free tier.
        This is why VOICE_PROVIDER=groq is recommended for Feature 10 STT.

        Args:
            audio_bytes: Raw audio data (wav, mp3, m4a, webm, etc.)
            filename:    Used to infer the audio format (e.g. "audio.webm").
        """
        import io

        client = openai.AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        response = await client.audio.transcriptions.create(
            model=settings.stt_model or "whisper-large-v3",
            file=audio_file,
        )
        return response.text

    async def synthesize_speech(self, text: str, voice: str = "default") -> bytes:
        raise NotImplementedError(
            "Groq does not currently support text-to-speech. "
            "Set VOICE_PROVIDER=openai for TTS, while keeping LLM_PROVIDER=groq "
            "for chat and STT. Both can be set simultaneously — see .env.example."
        )
