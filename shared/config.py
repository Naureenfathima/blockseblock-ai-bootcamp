"""
Centralized configuration for the AI Engineering Bootcamp.

All environment variables are read here. No other file in this project should
call os.getenv() directly — import `settings` from this module instead.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and the .env file."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        env_file_encoding="utf-8",
        # Unknown env vars in .env are silently ignored — students can have
        # provider-specific vars set without breaking providers they aren't using.
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Provider routing
    # -------------------------------------------------------------------------

    # Which provider to use for chat/agents/RAG.
    # Valid values: "openai", "anthropic", "cohere", "ollama", "custom"
    llm_provider: str = "openai"

    # Optional: use a different provider for voice (STT/TTS) in Feature 10.
    # Defaults to llm_provider if not set.
    voice_provider: str = ""

    # -------------------------------------------------------------------------
    # OpenAI
    # -------------------------------------------------------------------------
    openai_api_key: str = ""
    # Leave blank to use the default OpenAI API endpoint.
    openai_base_url: str = ""
    openai_model: str = "gpt-4o-mini"

    # -------------------------------------------------------------------------
    # Anthropic
    # -------------------------------------------------------------------------
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # -------------------------------------------------------------------------
    # Cohere
    # -------------------------------------------------------------------------
    cohere_api_key: str = ""
    cohere_model: str = "command-r-plus"

    # -------------------------------------------------------------------------
    # Ollama (local — no API key needed)
    # -------------------------------------------------------------------------
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # -------------------------------------------------------------------------
    # Custom OpenAI-compatible endpoint
    # -------------------------------------------------------------------------
    custom_base_url: str = ""
    custom_api_key: str = ""
    custom_model: str = ""

    # -------------------------------------------------------------------------
    # Vector database (Feature 5+)
    # -------------------------------------------------------------------------
    vector_db_path: str = "./data/vectordb"
    embedding_model: str = "text-embedding-3-small"

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    app_port: int = 8000
    app_host: str = "0.0.0.0"

    # -------------------------------------------------------------------------
    # Session management (Feature 3+)
    # -------------------------------------------------------------------------
    session_ttl_seconds: int = 3600

    # -------------------------------------------------------------------------
    # Rate limiting (Feature 12)
    # -------------------------------------------------------------------------
    rate_limit_per_minute: int = 60

    # -------------------------------------------------------------------------
    # Domain / assistant identity
    # -------------------------------------------------------------------------
    assistant_name: str = "My AI Assistant"
    assistant_description: str = (
        "You are a helpful assistant. Replace this with your domain description."
    )

    def effective_voice_provider(self) -> str:
        """Return the provider to use for voice features.

        Falls back to the main LLM provider if VOICE_PROVIDER is not set,
        so students using a speech-capable provider everywhere don't need
        to set this separately.
        """
        return self.voice_provider or self.llm_provider


# Single shared instance — import this object, don't instantiate Settings yourself.
settings = Settings()
