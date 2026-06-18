# Feature 3: AI Memory

**Week 1 · Phase: Brain**

---

## What You'll Build

Right now, each message you send is a fresh start — the assistant remembers nothing from the previous message. Feature 3 fixes that. You'll build a session system: when a user starts a conversation, a session is created to hold the message history. Every subsequent message in that session is sent to the LLM *with* the full prior conversation as context, so the assistant can refer back to anything said earlier.

By the end, the sidebar shows all your conversations, clicking one reloads its history, and hitting "New Chat" starts a clean session. This is the memory layer that everything else in the course builds on.

---

## Concepts Covered

| Term | Where to look |
|------|--------------|
| Session | [GLOSSARY.md — Session](../../../GLOSSARY.md#session) |
| Context Window | [GLOSSARY.md — Context Window](../../../GLOSSARY.md#context-window) |
| Token (context cost) | [GLOSSARY.md — Token](../../../GLOSSARY.md#token) |
| Stateless vs Stateful | This README — see below |
| Sliding window | `solution/main.py` — `CONTEXT_WINDOW_SIZE` |
| LLMResponse | `shared/providers/base.py` — the normalized response object returned by `call_llm()` |

**Stateless vs Stateful:**  
Features 1 and 2 are *stateless* — the server treats every request as if it never saw the user before. Feature 3 makes the app *stateful* — the server now holds data (sessions) between requests. This is a fundamental shift in how the backend works, and introduces the need for storage, cleanup, and context management.

**Why `result.content`, not `result.choices[0].message.content`:**  
`call_llm()` returns a `LLMResponse` object (defined in `shared/providers/base.py`), not a raw OpenAI response. `result.content` is the normalized text accessor that works identically for every provider — OpenAI, Groq, Anthropic, Ollama, Azure, Bedrock, Vertex. Never use `result.choices[0].message.content` — that's a raw OpenAI-only pattern that will crash on any other provider.

---

## How to Run It

1. Navigate to the starter folder:

```bash
cd week-1-brain/feature-3-ai-memory/starter
```

2. Start the server:

```bash
uvicorn main:app --reload --port 8000
```

3. Features 1 and 2 work immediately. Session endpoints (`/api/sessions/*`) raise errors until you complete the steps below.

4. Open `http://localhost:8000` — the sidebar appears. "New Chat" and session loading are wired once your implementation is complete.

---

## Your Task

**Step 1–5:** Open `starter/session_store.py` and implement the four functions. Each has a detailed docstring explaining what to write:

- [ ] `create_session()` — generate a UUID, create a `Session`, store it in `_store`
- [ ] `get_session(id)` — return `_store.get(id)`
- [ ] `add_message(id, role, content)` — append a `Message` to the session
- [ ] `list_sessions()` — return sessions sorted newest-first

**Step 6–7:** Open `starter/main.py` and implement the four session endpoints:

- [ ] `POST /api/sessions` — call `create_session()`, return `{"session_id": ...}`
- [ ] `GET /api/sessions` — call `list_sessions()`, build `SessionSummary` list
- [ ] `POST /api/sessions/{id}/chat` — load history, apply sliding window (Step 7), call LLM, save both messages, return `StructuredResponse`
- [ ] `GET /api/sessions/{id}/history` — return `session.messages`

**Test with a multi-turn conversation:**

- [ ] Start a new session via the "New Chat" button (or `POST /api/sessions` in Swagger)
- [ ] Have at least 5 exchanges
- [ ] In message 3 or later, reference something from message 1 (e.g. "going back to what I asked about hiking boots…")
- [ ] Confirm the assistant answers correctly — it should remember the earlier context
- [ ] Start a second session and confirm it has no memory of the first
- [ ] **Provider-switch test:** change `LLM_PROVIDER` in `.env` to a different provider (e.g. `groq` → `ollama`, or `openai` → `groq`) and repeat a multi-turn conversation — session memory should work identically, because `session_store.py` is provider-agnostic and `result.content` works the same for every provider

---

## Stretch Challenges

1. **Test the sliding window** — set `CONTEXT_WINDOW_SIZE = 4`, have a 6-message conversation, then ask about something from message 1. What happens? Why?
2. **Session titles** — right now the title is the first user message. Change `new_session()` to accept an optional `title` parameter, and let users name their sessions.
3. **Delete a session** — add `DELETE /api/sessions/{id}` that removes the session from `_store` and add a delete button in the sidebar.
4. **Message timestamps** — the `Message` model has a `timestamp` field. Render each message bubble with a relative time label ("2 min ago") in the UI.

---

## Framework Bridge

> **What you built vs. what frameworks call it**
>
> | What you built in this course | LangChain equivalent |
> |-------------------------------|----------------------|
> | `session_store.py` — in-memory dict of sessions | `ConversationBufferMemory` |
> | `messages[-CONTEXT_WINDOW_SIZE:]` sliding window | `ConversationBufferWindowMemory(k=20)` |
> | `GET /api/sessions/{id}/history` | `.load_memory_variables({})["history"]` |
> | `add_message(id, "user", ...)` + `add_message(id, "assistant", ...)` | `memory.save_context({"input": ...}, {"output": ...})` |
>
> This course builds these patterns from scratch so you understand what LangChain is wrapping. Once you understand the internals, using LangChain becomes a shortcut rather than a black box. See Resource 3 for the full equivalents table and a SQLite upgrade sketch.

---

## Week 1 Complete 🎉

> ### What your app can do right now
>
> You have built a working AI assistant with three cumulative capabilities:
>
> ```
> ┌─────────────────────────────────────────────────────────────┐
> │                    YOUR AI ASSISTANT                        │
> │                                                             │
> │  Browser (ui/)                                              │
> │    ├── Chat panel  ──────────────────→  POST /api/chat      │
> │    ├── Structured Mode toggle  ──────→  POST /api/chat/     │
> │    │                                        structured      │
> │    └── Session sidebar  ────────────→  POST /api/sessions/  │
> │                                             {id}/chat       │
> │                                                             │
> │  FastAPI (main.py)                                          │
> │    ├── Feature 1: plain chat  (stateless)                   │
> │    ├── Feature 2: structured JSON + intent classification   │
> │    └── Feature 3: sessions + history + sliding window       │
> │                                                             │
> │  Shared infrastructure                                      │
> │    ├── shared/llm_client.py  (provider-agnostic)            │
> │    ├── shared/session_store.py  (in-memory dict)            │
> │    └── shared/models.py  (StructuredResponse, Session, …)   │
> │                                                             │
> │  LLM Provider  (configured in .env)                         │
> │    └── OpenAI / Anthropic / Cohere / Ollama                 │
> └─────────────────────────────────────────────────────────────┘
> ```
>
> **What's missing:** the assistant only knows what you tell it in the chat. It can't read your company's documents, policies, or product catalog. That changes in Week 2.

---

## What's Next

**Feature 4** begins Week 2: you'll add a document upload endpoint so the assistant can read files you provide. This is the first step toward RAG (Retrieval-Augmented Generation) — the technique that lets the assistant answer questions from *your* data rather than just its training data.

→ See [resource/memory-patterns-guide.md](resource/memory-patterns-guide.md) (Resource 3) for a comparison of memory strategies and a SQLite upgrade sketch.
