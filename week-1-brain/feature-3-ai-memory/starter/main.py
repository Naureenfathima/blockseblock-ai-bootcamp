"""
Feature 3: AI Memory — starter

Features 1 and 2 (/api/chat and /api/chat/structured) are complete and working.
Your job is to:
  Step 1–5: implement the four functions in session_store.py (this folder)
  Step 6:   implement the four session endpoints below
  Step 7:   implement context-window slicing in session_chat()

Run with:
    uvicorn main:app --reload --port 8000

The server starts and Features 1+2 work immediately. Session endpoints will
raise errors until you complete the steps above.
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

# Import from the LOCAL session_store.py (same folder) — this is the file
# you implement. The complete version is at shared/session_store.py for reference.
from session_store import add_message, create_session, get_session, list_sessions

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
    created_at: str
    message_count: int
    title: str


# ---------------------------------------------------------------------------
# Feature 1: Plain chat  (complete — do not modify)
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message and get a plain-text reply (stateless)."""
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
# Feature 2: Structured chat  (complete — do not modify)
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
    """Send a message and receive a structured response (stateless)."""
    messages = [
        {"role": "system", "content": _STRUCTURED_SYSTEM_PROMPT},
        {"role": "user", "content": request.message},
    ]
    result = await call_llm(messages, temperature=0.3, response_format={"type": "json_object"})
    return _parse_structured(result.content or "")


# ---------------------------------------------------------------------------
# Feature 3: Session management  ← YOUR WORK STARTS HERE
# ---------------------------------------------------------------------------

@app.post("/api/sessions")
async def new_session() -> dict:
    """
    Create a new session and return its ID.

    Steps:
      1. Call create_session() from session_store.py.
      2. Return {"session_id": <the id>}.

    After implementing, the sidebar's "New Chat" button will work.
    """
    # TODO (Feature 3, Step 6a): Implement new_session().
    # One line: session_id = create_session()
    # One line: return {"session_id": session_id}
    raise NotImplementedError("Implement new_session()")


@app.get("/api/sessions", response_model=list[SessionSummary])
async def sessions_list() -> list[SessionSummary]:
    """
    List all sessions, most recent first, as sidebar summaries.

    Steps:
      1. Call list_sessions() to get all Session objects.
      2. For each session, find the first user message (or use "New conversation").
      3. Truncate it to 60 characters for the sidebar title.
      4. Return a list of SessionSummary objects.

    Hint — find the first user message:
      next((m.content for m in s.messages if m.role == "user"), "")
    """
    # TODO (Feature 3, Step 6b): Implement sessions_list().
    raise NotImplementedError("Implement sessions_list()")


@app.post("/api/sessions/{session_id}/chat", response_model=StructuredResponse)
async def session_chat(session_id: str, request: ChatRequest) -> StructuredResponse:
    """
    Send a message within a session and get a structured reply with full history.

    Steps:
      1. Look up the session with get_session(session_id).
         If None, raise HTTPException(status_code=404, detail="...").

      2. Build the messages list:
           messages = [{"role": "system", "content": _STRUCTURED_SYSTEM_PROMPT}]

      3. Apply the sliding window:
           history = session.messages
           # TODO (Feature 3, Step 7): CONTEXT WINDOW MANAGEMENT
           # If len(history) > CONTEXT_WINDOW_SIZE, keep only the last
           # CONTEXT_WINDOW_SIZE messages:
           #   history = history[-CONTEXT_WINDOW_SIZE:]
           # This prevents the prompt from exceeding the model's context limit.
           # See resource/memory-patterns-guide.md for smarter approaches.

      4. Add each history message to `messages`:
           for msg in history:
               messages.append({"role": msg.role, "content": msg.content})

      5. Append the new user message:
           messages.append({"role": "user", "content": request.message})

      6. Persist the user message BEFORE calling the LLM:
           add_message(session_id, "user", request.message)

      7. Call the LLM:
           result = await call_llm(messages, temperature=0.3,
                                   response_format={"type": "json_object"})
         IMPORTANT: access the text as result.content (not result.choices[0].message.content).
         call_llm() returns a LLMResponse object — .content works for ALL providers
         (OpenAI, Groq, Anthropic, Ollama, etc.). choices[0] only works for raw OpenAI objects.

      8. Parse the result:
           structured = _parse_structured(result.content or "")

      9. Persist ONLY the answer text as the assistant's history entry
         (not the full JSON — clean history is better for context):
           add_message(session_id, "assistant", structured.answer)

      10. Return structured.
    """
    # TODO (Feature 3, Step 6c): Implement session_chat() following the steps above.
    raise NotImplementedError("Implement session_chat()")


@app.get("/api/sessions/{session_id}/history", response_model=list[Message])
async def session_history(session_id: str) -> list[Message]:
    """
    Return the full message history for a session.

    Steps:
      1. Look up with get_session(session_id); raise 404 if None.
      2. Return session.messages.
    """
    # TODO (Feature 3, Step 6d): Implement session_history().
    raise NotImplementedError("Implement session_history()")


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
        "groq": settings.groq_model,
        "azure": settings.azure_openai_deployment_name,
        "bedrock": settings.bedrock_model_id,
        "vertex": settings.vertex_model,
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
