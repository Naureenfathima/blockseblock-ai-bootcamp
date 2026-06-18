"""
In-memory session store for the AI Engineering Bootcamp.

This module provides a simple dictionary-based store for conversation sessions.
It is intentionally simple so students can understand the fundamentals before
moving to a database-backed solution.

IMPORTANT — LIMITATION:
  All sessions are lost when the server restarts. This is acceptable for
  development and demos, but not for production. See Resource 3
  (resource/memory-patterns-guide.md in feature-3-ai-memory/) for a comparison
  of memory strategies, including how to swap this out for SQLite or Postgres.

FRAMEWORK EQUIVALENTS (for students exploring LangChain after this course):
  This module is what LangChain calls ConversationBufferMemory.
  The sliding window in main.py (messages[-CONTEXT_WINDOW_SIZE:]) is what
  LangChain calls ConversationBufferWindowMemory.
  See Resource 3 for the full "What You Built vs What Frameworks Call It" table.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from shared.models import Message, Session

# The store: a plain dict mapping session_id (str) -> Session.
# Module-level so it persists for the lifetime of the server process.
_store: dict[str, Session] = {}


def create_session() -> str:
    """
    Create a new empty session and return its ID.

    Each session gets a random UUID so IDs are collision-free without a
    database sequence. The created_at timestamp is recorded in UTC.
    """
    session_id = str(uuid.uuid4())
    _store[session_id] = Session(
        id=session_id,
        created_at=datetime.now(tz=timezone.utc),
        messages=[],
    )
    return session_id


def get_session(session_id: str) -> Optional[Session]:
    """
    Return the session with the given ID, or None if it doesn't exist.

    Callers should always check for None — a missing session should result in
    a 404 HTTP response, not a KeyError crash.
    """
    return _store.get(session_id)


def add_message(session_id: str, role: str, content: str) -> None:
    """
    Append a new message to an existing session's history.

    Silently does nothing if the session_id is not found — the endpoint is
    responsible for validating the session exists before calling this.

    Args:
        session_id: The session to append to.
        role:       "user" or "assistant".
        content:    The text of the message.
    """
    session = _store.get(session_id)
    if session is None:
        return

    session.messages.append(
        Message(
            role=role,  # type: ignore[arg-type]  # Literal checked by caller
            content=content,
            timestamp=datetime.now(tz=timezone.utc),
        )
    )


def list_sessions() -> list[Session]:
    """
    Return all sessions, most recently created first.

    The list is sorted by created_at descending so the sidebar shows the
    newest conversation at the top.
    """
    return sorted(_store.values(), key=lambda s: s.created_at, reverse=True)
