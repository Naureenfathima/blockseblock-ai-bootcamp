"""
Feature 2: Prompt Mastery — starter

Feature 1's /api/chat endpoint is complete and working — run this file and
you'll have a working chat server immediately. Your job is to implement
/api/chat/structured, which requires two things:
  1. A well-crafted system prompt that tells the model exactly what JSON to return.
  2. JSON parsing code that turns the model's text response into a StructuredResponse.

Steps:
  - Step 1: Write _STRUCTURED_SYSTEM_PROMPT (below)
  - Step 2: Parse the LLM result into a StructuredResponse in chat_structured()

Run with:
    uvicorn main:app --reload --port 8000
"""
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.llm_client import call_llm
from shared.models import StructuredResponse
from shared.provider_check import check_provider_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup checks before the server begins accepting requests."""
    await check_provider_config()
    yield


app = FastAPI(
    title="My AI BlockSeBlock Assistant",
    description="Domain-Specific AI Assistant — AI Engineering Bootcamp, BlockseBlock",
    version="2.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    """The body expected by POST /api/chat and POST /api/chat/structured."""

    message: str


class ChatResponse(BaseModel):
    """The body returned by POST /api/chat (plain text mode)."""

    response: str


# ---------------------------------------------------------------------------
# Feature 1: Plain chat  (complete — do not modify)
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message and get a plain-text reply (Feature 1, unchanged)."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant for [YOUR_DOMAIN]. "
                "Answer clearly and concisely. "
                "If you don't know something, say so honestly rather than guessing."
            ),
        },
        {"role": "user", "content": request.message},
    ]

    result = await call_llm(messages)
    return ChatResponse(response=result.content or "")


# ---------------------------------------------------------------------------
# Feature 2: Structured chat  ← YOUR WORK STARTS HERE
# ---------------------------------------------------------------------------

# TODO (Feature 2, Step 1): Write the system prompt.
#
# This prompt is the most important thing you write in this feature.
# It must instruct the model to return ONLY a JSON object (no markdown, no
# extra text) with exactly these four fields matching StructuredResponse:
#
#   "intent":         one of "general_question", "domain_question",
#                     "action_request", or "unclear"
#   "answer":         your plain-English reply to the user's message
#   "confidence":     a float between 0.0 and 1.0
#   "sources_needed": true or false
#
# Tips for a strong prompt:
#   - Define each intent value precisely so the model classifies consistently.
#   - Give confidence guidelines (e.g., what 0.9 vs 0.4 means).
#   - Say "respond ONLY with the JSON object" — say it twice if needed.
#   - Replace [YOUR_DOMAIN] with your actual domain.
#   - Shorter, more direct prompts usually outperform long rambling ones.
#
# See resource/prompt-engineering-workbook.md for worked examples and exercises.
_STRUCTURED_SYSTEM_PROMPT = """
# TODO (Feature 2, Step 1): Replace this string with your structured system prompt.
# The prompt should instruct the model to return JSON matching StructuredResponse.
# See the comments above for the required fields and tips.
"""


@app.post("/api/chat/structured", response_model=StructuredResponse)
async def chat_structured(request: ChatRequest) -> StructuredResponse:
    """
    Send a message and receive a structured response with intent classification.

    Your task: build the system prompt (Step 1 above) and parse the model's
    JSON reply into a StructuredResponse (Step 2 below).
    """
    messages = [
        {"role": "system", "content": _STRUCTURED_SYSTEM_PROMPT},
        {"role": "user", "content": request.message},
    ]

    result = await call_llm(
        messages,
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    raw_text = result.content or ""

    # TODO (Feature 2, Step 2): Parse raw_text into a StructuredResponse.
    #
    # 1. Parse the JSON:
    #      data = json.loads(raw_text)
    #
    # 2. Construct the Pydantic model:
    #      return StructuredResponse(**data)
    #
    # 3. Wrap both lines in a try/except — if the model returns invalid JSON,
    #    return a safe fallback so the server doesn't crash:
    #      return StructuredResponse(
    #          intent="unclear",
    #          answer=raw_text or "The assistant returned an unexpected response.",
    #          confidence=0.0,
    #          sources_needed=False,
    #      )
    #
    # The fallback is important: even with JSON mode enabled, some providers
    # may occasionally return malformed output, and a graceful degradation is
    # always better than a 500 error.
    pass


@app.get("/api/health")
async def health():
    """Quick liveness check — returns 200 OK if the server is running."""
    return {"status": "ok"}


@app.get("/api/provider-info")
async def provider_info():
    """Return which LLM and voice provider are currently active (no API keys)."""
    from shared.config import settings

    voice_name = settings.effective_voice_provider().lower().strip()
    llm_name = settings.llm_provider.lower().strip()

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


_ui_path = Path(__file__).resolve().parents[3] / "ui"
if _ui_path.exists():
    app.mount("/", StaticFiles(directory=str(_ui_path), html=True), name="ui")
