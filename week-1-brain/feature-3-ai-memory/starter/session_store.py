"""
Feature 3 starter: in-memory session store — YOUR IMPLEMENTATION GOES HERE.

The complete version lives in shared/session_store.py (read it for reference).
Your job is to implement the four functions below using a plain Python dict.

Why implement it yourself?
  Understanding dict-keyed stores is the foundation for everything that
  comes next: database-backed sessions (SQLite, Postgres), Redis caches,
  and vector stores all follow the same create / read / write / list pattern.
  Once you've built this by hand, swapping the backend is a 10-line change.

See resource/memory-patterns-guide.md for the full comparison and a SQLite sketch.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

# Import the models — these are shared and already complete.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.models import Message, Session

# TODO (Feature 3, Step 1): Create the in-memory store.
#
# Define a module-level dict called `_store` that maps session_id (str)
# to a Session object. It should start empty.
# Hint:  _store: dict[str, Session] = {}
_store: dict[str, Session] = {}   # ← already declared; implement the functions below


def create_session() -> str:
    """
    Create a new empty session and return its ID.

    Steps:
      1. Generate a random UUID string with str(uuid.uuid4()).
      2. Create a Session(id=..., created_at=datetime.now(tz=timezone.utc), messages=[]).
      3. Store it in _store under the session_id key.
      4. Return the session_id.
    """
    # TODO (Feature 3, Step 2): Implement create_session().
    # After implementing, POST /api/sessions should return a real UUID.
    raise NotImplementedError("Implement create_session() — see the docstring above.")


def get_session(session_id: str) -> Optional[Session]:
    """
    Return the Session for the given ID, or None if it doesn't exist.

    Steps:
      Use _store.get(session_id) — this returns None automatically if the
      key is missing, which is exactly what we want (the endpoint converts
      None into a 404 response).
    """
    # TODO (Feature 3, Step 3): Implement get_session().
    # Hint: one line — return _store.get(session_id)
    raise NotImplementedError("Implement get_session() — see the docstring above.")


def add_message(session_id: str, role: str, content: str) -> None:
    """
    Append a new Message to an existing session.

    Steps:
      1. Look up the session: session = _store.get(session_id).
      2. If session is None, return early (don't crash — the endpoint already
         validated the session exists before calling this).
      3. Create a Message(role=role, content=content, timestamp=datetime.now(tz=timezone.utc)).
      4. Append it to session.messages.
    """
    # TODO (Feature 3, Step 4): Implement add_message().
    # After implementing, conversation history will be saved and the AI will
    # remember earlier messages within the session.
    raise NotImplementedError("Implement add_message() — see the docstring above.")


def list_sessions() -> list[Session]:
    """
    Return all sessions, most recently created first.

    Steps:
      Return sorted(_store.values(), key=lambda s: s.created_at, reverse=True)
    """
    # TODO (Feature 3, Step 5): Implement list_sessions().
    # After implementing, the sidebar will populate with your session history.
    raise NotImplementedError("Implement list_sessions() — see the docstring above.")
