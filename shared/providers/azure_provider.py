"""
Provider implementation for Azure OpenAI.

Azure OpenAI = the same underlying models (GPT-4o, etc.) but running inside
Microsoft's data centers. Your data doesn't leave Azure's infrastructure.
Required for many enterprise, healthcare, and government customers due to
data residency, compliance, and existing Azure billing agreements.

To use this provider, set in .env:
  LLM_PROVIDER=azure
  AZURE_OPENAI_API_KEY=your_key_here
  AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
  AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name  # NOT the model name
  AZURE_OPENAI_API_VERSION=2024-02-01

Note on DEPLOYMENT_NAME: in Azure AI Studio you create a "deployment" of a
model (e.g., deploy gpt-4o as "my-gpt4o-deployment"). The deployment name
is what you set here, not the underlying model name.
"""
from typing import Optional, List

import openai

from shared.config import settings
from shared.providers.base import LLMProvider, LLMResponse
from shared.providers.openai_provider import OpenAIProvider


class AzureProvider(OpenAIProvider):
    """
    Azure OpenAI via the `openai` package's AzureOpenAI client.

    Inherits all request/response logic from OpenAIProvider — tool calling,
    JSON mode, and streaming all work identically. The only difference is
    the client constructor (AzureOpenAI instead of OpenAI) and the use of
    a deployment name rather than a model name.
    """

    def __init__(self) -> None:
        # AzureOpenAI requires endpoint + api_version in the constructor;
        # the deployment name is passed as the model parameter per request.
        self._client = openai.AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
        )
        # The "model" for Azure is the deployment name, not the underlying model.
        self._model = settings.azure_openai_deployment_name
        self._provider_name = "azure"

    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        raise NotImplementedError(
            "Azure OpenAI does not expose a speech transcription endpoint "
            "through this provider. For voice features, set VOICE_PROVIDER=openai "
            "or implement Azure AI Speech separately. "
            "See docs/provider-setup-guide.md for options."
        )

    async def synthesize_speech(self, text: str, voice: str = "default") -> bytes:
        raise NotImplementedError(
            "Azure OpenAI does not expose a TTS endpoint through this provider. "
            "Set VOICE_PROVIDER=openai for voice features. "
            "See docs/provider-setup-guide.md for options."
        )
