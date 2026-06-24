"""
Feature 4: Feed the Brain — solution

Adds document ingestion on top of Feature 3's session chat. Users upload
.txt, .pdf, and .docx files; the server extracts text, chunks it using a
selectable strategy, and stores the chunks. The Documents tab in the UI
shows uploaded files, their status, chunk counts, strategy used, and lets
students inspect individual chunks (with page numbers for the page strategy).

Two chunking strategies are available via the `strategy` upload parameter:
  "sentence"  — sentence-aware fixed-size (default, works for everything)
  "paragraph" — paragraph-based (best for formal structured documents)

New endpoints vs Feature 3:
  POST /api/documents/upload        — multipart: file + optional strategy field
  GET  /api/documents               — list documents with status, chunks, strategy
  DELETE /api/documents/{id}        — remove document and its chunks
  GET  /api/documents/{id}/chunks   — inspect chunks (with page_number when available)

All Feature 3 endpoints remain unchanged.

Run with:
    uvicorn main:app --reload --port 8000
"""
import json
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.document_store import (
    delete_document,
    get_chunks,
    get_document,
    list_documents,
    save_chunk,
    save_document,
    update_document,
)
from shared.ingestion import CHUNKING_STRATEGIES, extract_pages, extract_text
from shared.llm_client import call_llm
from shared.models import Chunk, Document, Message, StructuredResponse
from shared.provider_check import check_provider_config
from shared.session_store import add_message, create_session, get_session, list_sessions

CONTEXT_WINDOW_SIZE = 20


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup checks before the server begins accepting requests."""
    await check_provider_config()
    yield


app = FastAPI(
    title="My AI BlockSeBlock Assistant",
    description="Domain-Specific AI Assistant — AI Engineering Bootcamp, BlockseBlock",
    version="4.0.0",
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
# Feature 3: Session management  (kept verbatim — convention #3)
# ---------------------------------------------------------------------------

@app.post("/api/sessions")
async def new_session() -> dict:
    """Start a new conversation session."""
    session_id = create_session()
    return {"session_id": session_id}


@app.get("/api/sessions", response_model=list[SessionSummary])
async def sessions_list() -> list[SessionSummary]:
    """List all sessions, most recent first."""
    summaries = []
    for s in list_sessions():
        first_user_msg = next((m.content for m in s.messages if m.role == "user"), "")
        title = (first_user_msg[:60] + "…") if len(first_user_msg) > 60 else (first_user_msg or "New conversation")
        summaries.append(SessionSummary(
            id=s.id,
            created_at=s.created_at.isoformat(),
            message_count=len(s.messages),
            title=title,
        ))
    return summaries


@app.post("/api/sessions/{session_id}/chat", response_model=StructuredResponse)
async def session_chat(session_id: str, request: ChatRequest) -> StructuredResponse:
    """Send a message within a session and get a structured reply."""
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    messages: list[dict] = [{"role": "system", "content": _STRUCTURED_SYSTEM_PROMPT}]
    history = session.messages
    if len(history) > CONTEXT_WINDOW_SIZE:
        history = history[-CONTEXT_WINDOW_SIZE:]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})

    add_message(session_id, "user", request.message)
    result = await call_llm(messages, temperature=0.3, response_format={"type": "json_object"})
    structured = _parse_structured(result.content or "")
    add_message(session_id, "assistant", structured.answer)
    return structured


@app.get("/api/sessions/{session_id}/history", response_model=list[Message])
async def session_history(session_id: str) -> list[Message]:
    """Return the full message history for a session."""
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session.messages


# ---------------------------------------------------------------------------
# Feature 4: Document ingestion
# ---------------------------------------------------------------------------

@app.post("/api/documents/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    strategy: str = Form("sentence"),
) -> Document:
    """
    Upload a document, extract its text, chunk it, and store the chunks.

    Form fields:
      file     — the uploaded file (.txt, .pdf, .docx)
      strategy — chunking strategy: "sentence" (default) or "paragraph"

    Flow:
      1. Validate strategy name.
      2. Create a Document record (status='processing').
      3. Extract text.
      4. Run the selected chunking strategy.
      5. Save each chunk with metadata (filename, chunk_index, strategy).
      6. Update Document to status='ready' with final chunk_count and strategy.
    """
    if strategy not in CHUNKING_STRATEGIES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown strategy '{strategy}'. Choose one of: {', '.join(CHUNKING_STRATEGIES)}.",
        )

    filename = file.filename or "unknown"
    doc = save_document(filename)

    try:
        file_bytes = await file.read()
        text = extract_text(file_bytes, filename)
        pages = extract_pages(file_bytes, filename)

        chunk_dicts = CHUNKING_STRATEGIES[strategy](text, pages)

        for cd in chunk_dicts:
            save_chunk(Chunk(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                text=cd["text"],
                chunk_index=cd["chunk_index"],
                metadata={
                    "filename": filename,
                    "chunk_index": cd["chunk_index"],
                    "page_number": cd.get("page_number"),
                    "strategy": strategy,
                },
            ))

        update_document(
            doc.id,
            status="ready",
            chunk_count=len(chunk_dicts),
            chunking_strategy=strategy,
        )
    except Exception as exc:
        update_document(doc.id, status="error", chunk_count=0, chunking_strategy=strategy)
        raise HTTPException(status_code=422, detail=str(exc))

    return get_document(doc.id)  # type: ignore[return-value]


@app.get("/api/documents", response_model=list[Document])
async def documents_list() -> list[Document]:
    """List all uploaded documents with status, chunk count, and strategy."""
    return list_documents()


@app.delete("/api/documents/{doc_id}")
async def remove_document(doc_id: str) -> dict:
    """Delete a document and all its chunks."""
    if not delete_document(doc_id):
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return {"deleted": doc_id}


@app.get("/api/documents/{doc_id}/chunks", response_model=list[Chunk])
async def document_chunks(doc_id: str) -> list[Chunk]:
    """Return all chunks for a document — useful for inspecting chunk quality."""
    if get_document(doc_id) is None:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return get_chunks(doc_id)


# ---------------------------------------------------------------------------
# Health + provider info
# ---------------------------------------------------------------------------

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
