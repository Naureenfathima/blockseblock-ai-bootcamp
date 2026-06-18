"""
Feature 3: AI Memory — solution

Adds persistent (within a server session) conversation history. Users can
start multiple chat sessions, switch between them, and the assistant will
remember everything said earlier in each conversation.

New endpoints vs Feature 2:
  POST /api/sessions                      — create a new session
  GET  /api/sessions                      — list all sessions
  POST /api/sessions/{id}/chat            — chat within a session (with history)
  GET  /api/sessions/{id}/history         — retrieve full message history

Feature 1 (/api/chat) and Feature 2 (/api/chat/structured) remain unchanged
for backward compatibility.

Run with:
    uvicorn main:app --reload --port 8000
"""
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.llm_client import call_llm
from shared.models import Message, Session, StructuredResponse
from shared.provider_check import check_provider_config
from shared.session_store import add_message, create_session, get_session, list_sessions

# Maximum number of past messages passed to the LLM per turn.
# Simple sliding window: if history > this limit, we keep only the most recent
# messages. See resource/memory-patterns-guide.md for smarter alternatives
# (summarization, embedding-based retrieval) that preserve older context cheaply.
CONTEXT_WINDOW_SIZE = 20


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup checks before the server begins accepting requests."""
    await check_provider_config()
    yield


app = FastAPI(
    title="My AI BlockSeBlock Assistant",
    description="Domain-Specific AI Assistant — AI Engineering Bootcamp, BlockseBlock",
    version="3.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    """The body expected by chat endpoints."""

    message: str


class ChatResponse(BaseModel):
    """The body returned by POST /api/chat (plain text mode)."""

    response: str


class SessionSummary(BaseModel):
    """A lightweight session descriptor for the sidebar list."""

    id: str
    created_at: str          # ISO-8601 string — easier to format in JS
    message_count: int
    title: str               # first user message, truncated; "New conversation" if empty


# ---------------------------------------------------------------------------
# Feature 1: Plain chat  (kept verbatim — convention #3)
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message and get a plain-text reply (stateless — no history)."""
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
# Feature 2: Structured chat  (kept verbatim — convention #3)
# ---------------------------------------------------------------------------

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


def _parse_structured(raw_text: str) -> StructuredResponse:
    """Parse raw LLM text into a StructuredResponse, with a safe fallback."""
    try:
        return StructuredResponse(**json.loads(raw_text))
    except Exception:
        return StructuredResponse(
            intent="unclear",
            answer=raw_text or "The assistant returned an unexpected response.",
            confidence=0.0,
            sources_needed=False,
        )


@app.post("/api/chat/structured", response_model=StructuredResponse)
async def chat_structured(request: ChatRequest) -> StructuredResponse:
    """Send a message and receive a structured response (stateless — no history)."""
    messages = [
        {"role": "system", "content": _STRUCTURED_SYSTEM_PROMPT},
        {"role": "user", "content": request.message},
    ]
    result = await call_llm(messages, temperature=0.3, response_format={"type": "json_object"})
    return _parse_structured(result.content or "")


# ---------------------------------------------------------------------------
# Feature 3: Session management
# ---------------------------------------------------------------------------

@app.post("/api/sessions")
async def new_session() -> dict:
    """
    Start a new conversation session.

    Returns a session_id that the client uses as part of the URL for all
    subsequent messages in this conversation.
    """
    session_id = create_session()
    return {"session_id": session_id}


@app.get("/api/sessions", response_model=list[SessionSummary])
async def sessions_list() -> list[SessionSummary]:
    """
    List all sessions, most recent first.

    Returns lightweight summaries suitable for rendering a sidebar — the full
    message history is fetched separately via GET /api/sessions/{id}/history.
    """
    summaries = []
    for s in list_sessions():
        first_user_msg = next(
            (m.content for m in s.messages if m.role == "user"), ""
        )
        title = (first_user_msg[:60] + "…") if len(first_user_msg) > 60 else (first_user_msg or "New conversation")
        summaries.append(
            SessionSummary(
                id=s.id,
                created_at=s.created_at.isoformat(),
                message_count=len(s.messages),
                title=title,
            )
        )
    return summaries


@app.post("/api/sessions/{session_id}/chat", response_model=StructuredResponse)
async def session_chat(session_id: str, request: ChatRequest) -> StructuredResponse:
    """
    Send a message within a session and get a structured reply.

    The assistant receives the full conversation history as context, so it can
    refer back to anything said earlier in this session.

    Context window management: only the most recent CONTEXT_WINDOW_SIZE messages
    are sent to the LLM. Older messages are dropped from the prompt (but kept
    in the stored history). This is the simplest windowing strategy — see
    resource/memory-patterns-guide.md for smarter alternatives.
    """
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found. Create one with POST /api/sessions.")

    # Build the prompt: system instruction + recent history + new user message.
    messages: list[dict] = [{"role": "system", "content": _STRUCTURED_SYSTEM_PROMPT}]

    history = session.messages
    if len(history) > CONTEXT_WINDOW_SIZE:
        # Keep only the tail of the history so the prompt fits in the context window.
        history = history[-CONTEXT_WINDOW_SIZE:]

    for msg in history:
        # We store only the answer text (not the full JSON) as the assistant's
        # history entry — this keeps conversation flow natural and token-efficient.
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": request.message})

    # Persist the user's message first so it's captured even if the LLM call fails.
    add_message(session_id, "user", request.message)

    # Note: if using an Ollama SLM without JSON mode support, the provider
    # falls back to plain text — _parse_structured's try/except handles that
    # gracefully (intent="unclear", confidence=0.0). See docs/slm-guide.md
    # for which local models support JSON mode reliably.
    result = await call_llm(messages, temperature=0.3, response_format={"type": "json_object"})
    structured = _parse_structured(result.content or "")  # LLMResponse.content — works for all providers

    # Store only the human-readable answer as the assistant turn — the structured
    # metadata (intent, confidence) is per-turn UI data, not needed in history.
    add_message(session_id, "assistant", structured.answer)

    return structured


@app.get("/api/sessions/{session_id}/history", response_model=list[Message])
async def session_history(session_id: str) -> list[Message]:
    """
    Return the full message history for a session.

    Used by the UI when the user clicks a session in the sidebar to reload
    its conversation into the chat area.
    """
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session.messages


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
