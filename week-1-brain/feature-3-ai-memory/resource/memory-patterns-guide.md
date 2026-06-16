# Resource 3: Memory Patterns Guide

**Feature 3 · AI Engineering Bootcamp · BlockseBlock**

The session store we built in Feature 3 is the simplest possible implementation.
This guide explains three progressively more capable memory strategies, when to use each, and how to upgrade when you need more.

---

## The Three Strategies

### Strategy 1: In-Memory Dictionary (what we built)

**How it works:** Sessions are stored in a Python dict that lives in RAM for the lifetime of the server process. When the server restarts, all sessions vanish.

```
User A  →  POST /api/sessions  →  _store["abc-123"] = Session(...)
User A  →  POST /api/sessions/abc-123/chat  →  _store["abc-123"].messages.append(...)
Server restarts  →  _store = {}  ← everything gone
```

**What we implemented:**

```python
_store: dict[str, Session] = {}  # lives in RAM only

def create_session() -> str:
    session_id = str(uuid.uuid4())
    _store[session_id] = Session(id=session_id, created_at=..., messages=[])
    return session_id

def add_message(session_id, role, content):
    _store[session_id].messages.append(Message(role=role, content=content, ...))
```

---

### Strategy 2: Database-Backed (SQLite or Postgres)

**How it works:** Sessions and messages are written to a database file (SQLite) or a running database server (Postgres). Data survives restarts, can be queried, and can be shared across multiple server processes.

**When to upgrade:** As soon as you need sessions to survive a restart, or when you're deploying on a server (Docker, cloud).

**The interface stays the same** — only the internals of `session_store.py` change.

```python
# With SQLite (using SQLAlchemy or raw sqlite3):

import sqlite3

_db = sqlite3.connect("sessions.db", check_same_thread=False)
_db.execute("""
    CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, created_at TEXT)
""")
_db.execute("""
    CREATE TABLE IF NOT EXISTS messages
    (id INTEGER PRIMARY KEY, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)
""")
_db.commit()

def create_session() -> str:
    session_id = str(uuid.uuid4())
    _db.execute("INSERT INTO sessions VALUES (?, ?)", (session_id, datetime.now().isoformat()))
    _db.commit()
    return session_id

def add_message(session_id: str, role: str, content: str) -> None:
    _db.execute(
        "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.now().isoformat())
    )
    _db.commit()

def get_session(session_id: str):
    row = _db.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    if not row:
        return None
    msgs = _db.execute(
        "SELECT role, content, timestamp FROM messages WHERE session_id=? ORDER BY timestamp",
        (session_id,)
    ).fetchall()
    return Session(
        id=row[0],
        created_at=datetime.fromisoformat(row[1]),
        messages=[Message(role=m[0], content=m[1], timestamp=datetime.fromisoformat(m[2])) for m in msgs]
    )
```

This is not required for the course — it's shown so you can see exactly how small the change is.

For production, consider:
- **SQLite** for a single-server deployment (simple, no separate process)
- **PostgreSQL** for multi-server or heavy load (more powerful, runs as a service)
- **SQLAlchemy** (ORM) to avoid writing raw SQL

---

### Strategy 3: Summary-Based Memory

**How it works:** Instead of sending the full message history to the LLM on every turn (which gets expensive and eventually exceeds the context window), the system periodically *summarizes* old messages and stores only the summary.

```
Turn 1–10:  stored verbatim
Turn 11:    system calls LLM: "Summarize this conversation in 3 sentences."
             → "The user asked about hiking boots, then discussed return policy,
                then asked about waterproofing. Key facts: size 12, £120 budget."
Turn 12+:   prompt = [system] + [summary] + [last 5 messages]
             (not the full 10-message history)
```

**Why it matters:** A context window has a fixed token limit (e.g., 128k tokens for GPT-4o). A long conversation can easily hit this. Summarization compresses old context into a few sentences, keeping the prompt small while preserving the most important facts.

**Trade-off:** The summary may lose nuance. If the user said something important in message 3 that the summary omitted, the model won't remember it by message 50.

**When to use:** Multi-session conversations that go on for a long time (customer service, research assistants, tutors). Not needed for most short-session apps.

---

## Comparison Table

| | In-Memory Dict | Database-Backed | Summary-Based |
|--|---|---|---|
| **Persistence** | None (resets on restart) | Full (survives restarts) | Full (summaries stored) |
| **Setup complexity** | Zero | Low (SQLite) / Medium (Postgres) | Medium–High |
| **Context window cost** | Grows with history | Grows with history | Bounded (summary + recent) |
| **Token cost per turn** | Increases every message | Increases every message | Stays roughly constant |
| **Information loss** | None | None | Some (summary may miss detail) |
| **Best for** | Dev, demos, Feature 3 | Production apps (Week 4) | Very long conversations |
| **Introduced in course** | Feature 3 | Feature 11 (Docker/deploy) | Optional stretch |

---

## The Sliding Window We Built

The `CONTEXT_WINDOW_SIZE = 20` limit in `solution/main.py` is Strategy 1.5 — still in-memory, but with a cap on how much history is sent to the LLM:

```python
history = session.messages
if len(history) > CONTEXT_WINDOW_SIZE:
    history = history[-CONTEXT_WINDOW_SIZE:]  # keep only the last 20
```

**What this loses:** if your session has 30 messages and you ask about something from message 2, the model won't see it — messages 1–10 were dropped.

**How summarization fixes this:** instead of dropping messages 1–10, you first ask the LLM to summarize them, store the summary, and include the summary in place of the raw messages. The model gets the gist of the early conversation without paying the token cost of all 10 messages verbatim.

---

## Choosing Your Strategy

```
Does the app need to survive a server restart?
  No  →  In-memory dict (Strategy 1). Fine for demos and Week 1–3.
  Yes →  Database-backed (Strategy 2). Add this in Feature 11 (Docker).

Will conversations regularly exceed 20–30 messages?
  No  →  Sliding window is fine.
  Yes →  Add summarization (Strategy 3) as a stretch goal.
```

For most students finishing this bootcamp: Strategy 1 now, Strategy 2 in Week 4 when you containerize. Strategy 3 is a stretch for anyone building a customer-facing product.
