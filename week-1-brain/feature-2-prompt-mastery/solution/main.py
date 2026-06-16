"""
Feature 2: Prompt Mastery — solution

Adds structured output to the assistant: a new endpoint that classifies the
user's intent, estimates confidence, and returns a rich JSON response instead
of plain text. Feature 1's /api/chat endpoint is kept untouched so both modes
are available simultaneously.

Run this with:
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000 to use the chat UI with the Structured Mode
toggle, or http://localhost:8000/docs to explore both endpoints interactively.
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
# Feature 1: Plain chat  (kept verbatim — convention #3)
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the AI assistant and get a plain-text reply.

    This endpoint is unchanged from Feature 1 — it exists here so students can
    run this folder standalone without needing the Feature 1 folder at all.
    """
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
# Feature 2: Structured chat
# ---------------------------------------------------------------------------

# This system prompt is the core lesson of Feature 2: crafting a prompt that
# produces reliably parseable JSON output. The field names must match
# StructuredResponse exactly; the descriptions help the model fill each field
# correctly even when the user's query is ambiguous.
_STRUCTURED_SYSTEM_PROMPT = """You are a helpful AI assistant for [YOUR_DOMAIN].

For every user message, respond ONLY with a JSON object (no markdown, no extra text)
with exactly these four fields:

{
  "intent": "<one of: general_question | domain_question | action_request | unclear>",
  "answer": "<your response to the user, written in plain English>",
  "confidence": <a number between 0.0 and 1.0 representing how sure you are>,
  "sources_needed": <true if domain documents would improve this answer, false otherwise>
}

Intent definitions:
- "general_question": factual/knowledge query not specific to [YOUR_DOMAIN]
- "domain_question": a question specifically about [YOUR_DOMAIN] and its offerings
- "action_request": the user wants something DONE (book, schedule, find, order, send…)
- "unclear": ambiguous, nonsensical, or doesn't fit the other categories

Confidence guidelines:
- 0.9–1.0: you are certain (common knowledge, clear domain fact)
- 0.6–0.8: you are reasonably sure but the user should verify
- 0.3–0.5: you are uncertain; the answer may be incomplete or partly guessed
- 0.0–0.2: you don't know and are mostly guessing

Respond ONLY with the JSON object. No preamble, no explanation, no markdown fences."""


@app.post("/api/chat/structured", response_model=StructuredResponse)
async def chat_structured(request: ChatRequest) -> StructuredResponse:
    """
    Send a message and receive a structured response with intent classification.

    The assistant analyzes the query, classifies its intent, answers it, and
    returns a confidence score — all as a validated JSON object. This is more
    useful than plain text for building UIs that react to the *type* of question
    (e.g., routing action requests, flagging low-confidence answers for review).

    If the model returns malformed JSON, we fall back to an 'unclear' response
    rather than crashing — the raw text is preserved in the 'answer' field so
    nothing is silently lost.
    """
    messages = [
        {"role": "system", "content": _STRUCTURED_SYSTEM_PROMPT},
        {"role": "user", "content": request.message},
    ]

    result = await call_llm(
        messages,
        temperature=0.3,   # lower temperature for more consistent JSON structure
        response_format={"type": "json_object"},
    )

    raw_text = result.content or ""

    try:
        data = json.loads(raw_text)
        return StructuredResponse(**data)
    except (json.JSONDecodeError, Exception):
        # The model produced something we can't parse. Return a degraded-but-safe
        # response rather than a 500 — the raw text is preserved so the student
        # can see what went wrong and improve their system prompt.
        return StructuredResponse(
            intent="unclear",
            answer=raw_text or "The assistant returned an unexpected response.",
            confidence=0.0,
            sources_needed=False,
        )


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
