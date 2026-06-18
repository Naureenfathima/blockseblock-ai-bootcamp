"""
Provider implementation for GCP Vertex AI.

GCP Vertex AI = Gemini and other models inside Google Cloud. Tight integration
with BigQuery, Cloud Storage, and other GCP services. Preferred when the rest
of your stack is already on GCP. Uses Application Default Credentials (ADC) —
no API key file needed if you're running inside GCP; run `gcloud auth
application-default login` locally.

Vertex AI now exposes an OpenAI-compatible endpoint for Gemini models, so this
provider reuses OpenAIProvider logic pointed at the Vertex endpoint.

To use this provider, set in .env:
  LLM_PROVIDER=vertex
  GCP_PROJECT_ID=your-project-id
  GCP_REGION=us-central1
  VERTEX_MODEL=google/gemini-2.0-flash-001

Then authenticate:
  gcloud auth application-default login
  # or set GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

Requires google-auth package: pip install google-auth
"""
from typing import Optional, List

from shared.config import settings
from shared.providers.base import LLMProvider, LLMResponse
from shared.providers.openai_provider import OpenAIProvider


def _get_vertex_token() -> str:
    """
    Get a short-lived Bearer token from Google Application Default Credentials.

    Vertex AI's OpenAI-compatible endpoint uses Bearer token auth instead of
    an API key. This helper fetches and refreshes the token as needed.
    """
    try:
        import google.auth
        import google.auth.transport.requests
    except ImportError:
        raise ImportError(
            "google-auth is required for LLM_PROVIDER=vertex. "
            "Install it: pip install google-auth"
        )

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token


class VertexProvider(OpenAIProvider):
    """
    GCP Vertex AI via the OpenAI-compatible Gemini endpoint.

    Inherits all request/response logic from OpenAIProvider — the only
    differences are the base_url (pointing at Vertex's OpenAI-compatible
    endpoint) and Bearer token authentication (refreshed per request via ADC).
    """

    def __init__(self) -> None:
        project = settings.gcp_project_id
        region = settings.gcp_region or "us-central1"
        model = settings.vertex_model

        base_url = (
            f"https://{region}-aiplatform.googleapis.com/v1beta1/projects/"
            f"{project}/locations/{region}/endpoints/openapi"
        )

        # Token is fetched fresh on each construction; the OpenAI client will use
        # it as a Bearer token. For long-running servers, refresh logic should be
        # added here — this is sufficient for course purposes.
        token = _get_vertex_token()

        super().__init__(
            api_key=token,
            base_url=base_url,
            model=model,
        )
        self._provider_name = "vertex"

    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        raise NotImplementedError(
            "GCP Vertex AI does not provide speech transcription through this provider. "
            "For STT, use Google Cloud Speech-to-Text (a separate GCP service) or set "
            "VOICE_PROVIDER=groq or VOICE_PROVIDER=openai. "
            "See docs/provider-setup-guide.md for options."
        )

    async def synthesize_speech(self, text: str, voice: str = "default") -> bytes:
        raise NotImplementedError(
            "GCP Vertex AI does not provide TTS through this provider. "
            "For TTS, use Google Cloud Text-to-Speech (a separate GCP service) or set "
            "VOICE_PROVIDER=openai. "
            "See docs/provider-setup-guide.md for options."
        )
