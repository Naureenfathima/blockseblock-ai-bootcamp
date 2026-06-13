"""
Feature 1: Hello AI — solution

A minimal FastAPI app that takes a user message and returns a reply from
the configured LLM. This is the foundation every subsequent feature builds on.

Run this with:
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000/docs to try the API interactively,
or open http://localhost:8000 to use the chat UI.
"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Make shared/ importable when running from this feature's directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.llm_client import call_llm
from shared.provider_check import check_provider_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup checks before the server begins accepting requests."""
    await check_provider_config()
    yield


# Rename "My AI Assistant" to something meaningful for your domain.
# Example: "Alpine Trail Co. Assistant", "MediHelper", "HRBot"
app = FastAPI(
    title="My AI Assistant",  # TODO: rename this to your domain assistant's name
    description="Domain-Specific AI Assistant — AI Engineering Bootcamp, BlockseBlock",
    version="1.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    """The body expected by POST /api/chat."""

    message: str


class ChatResponse(BaseModel):
    """The body returned by POST /api/chat."""

    response: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the AI assistant and get a reply.

    The system prompt below defines who the assistant is.
    Replace [YOUR_DOMAIN] with your chosen domain — this is the single most
    impactful change you'll make in Feature 1.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant for [YOUR_DOMAIN]. "  # TODO: replace with your domain
                "Answer clearly and concisely. "
                "If you don't know something, say so honestly rather than guessing."
            ),
        },
        {"role": "user", "content": request.message},
    ]

    result = await call_llm(messages)
    return ChatResponse(response=result.content or "")


@app.get("/api/health")
async def health():
    """Quick liveness check — returns 200 OK if the server is running."""
    return {"status": "ok"}


@app.get("/api/provider-info")
async def provider_info():
    """
    Return which LLM and voice provider are currently active.
    Safe to expose publicly — never returns API keys.
    """
    from shared.config import settings

    voice_name = settings.effective_voice_provider().lower().strip()
    llm_name = settings.llm_provider.lower().strip()

    # Read the model name for whichever provider is active.
    model_map = {
        "openai": settings.openai_model,
        "anthropic": settings.anthropic_model,
        "cohere": settings.cohere_model,
        "ollama": settings.ollama_model,
        "custom": settings.custom_model,
    }

    return {
        "llm_provider": llm_name,
        "llm_model": model_map.get(llm_name, "unknown"),
        "voice_provider": voice_name if voice_name != llm_name else None,
        "voice_model": model_map.get(voice_name) if voice_name != llm_name else None,
    }


# ---------------------------------------------------------------------------
# Serve the UI — must come LAST so API routes take priority over static files.
# ---------------------------------------------------------------------------
_ui_path = Path(__file__).resolve().parents[3] / "ui"
if _ui_path.exists():
    app.mount("/", StaticFiles(directory=str(_ui_path), html=True), name="ui")
