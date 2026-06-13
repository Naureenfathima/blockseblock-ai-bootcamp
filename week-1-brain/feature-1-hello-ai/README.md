# Feature 1: Hello AI

**Week 1 · Phase: Brain**

---

## What You'll Build

By the end of this feature you'll have a live web server that accepts a message from a user and replies using a real AI model — your first working AI assistant endpoint. You'll also customize the assistant's personality with a system prompt tailored to your chosen domain.

---

## Concepts Covered

| Term | Where to look |
|------|--------------|
| LLM | [GLOSSARY.md — LLM](../../../GLOSSARY.md#llm-large-language-model) |
| API / Endpoint | [GLOSSARY.md — API](../../../GLOSSARY.md#api-application-programming-interface), [Endpoint](../../../GLOSSARY.md#endpoint) |
| JSON | [GLOSSARY.md — JSON](../../../GLOSSARY.md#json-javascript-object-notation) |
| System Prompt | [GLOSSARY.md — System Prompt](../../../GLOSSARY.md#system-prompt) |
| Token | [GLOSSARY.md — Token](../../../GLOSSARY.md#token) |
| Temperature | [GLOSSARY.md — Temperature](../../../GLOSSARY.md#temperature) |
| Provider | [GLOSSARY.md — Provider](../../../GLOSSARY.md#provider) |

---

## How to Run It

> Before you start, complete the setup in [SETUP.md](../../../SETUP.md).

1. Open a terminal and navigate to the `starter/` folder:

```bash
cd week-1-brain/feature-1-hello-ai/starter
```

2. Make sure your virtual environment is active (you'll see `(venv)` in the prompt).

3. Start the server:

```bash
uvicorn main:app --reload --port 8000
```

4. Open your browser to `http://localhost:8000/docs` — you should see the Swagger UI with `/api/chat` and `/api/health` listed.

5. The chat UI is at `http://localhost:8000` — it will load but `/api/chat` will return an error until you complete the TODOs.

---

## Your Task

Work through `starter/main.py` from top to bottom. There are two TODO comments — each one tells you exactly what to write in plain English.

- [ ] **Step 1** — Add `message: str` to `ChatRequest`
- [ ] **Step 2** — Implement the `chat()` function body: build the messages list, call `call_llm`, return the result
- [ ] **Personalize** — Replace `[YOUR_DOMAIN]` in the system prompt with your actual domain (e.g. "Alpine Trail Co., an outdoor gear retailer")
- [ ] **Test** — Ask 3 domain-specific questions through the chat UI or Swagger
- [ ] **Observe** — Note at least one thing the assistant gets wrong or makes up. This is why Week 2 exists.

---

## Stretch Challenges

Once the core is working:

1. **Change the temperature** — pass `temperature=0.2` to `call_llm` and ask the same question twice. Compare the results to `temperature=0.9`.
2. **Change `max_tokens`** — try `max_tokens=50`. What happens to long answers?
3. **Add a second system message rule** — e.g. "Always end your reply with a relevant follow-up question."

---

## What's Next

**Feature 2** adds a proper domain persona: a name, a tone, and structured responses — so your assistant stops sounding generic and starts sounding like it was built for your domain.

→ See [resource/setup-checklist.md](resource/setup-checklist.md) if you hit any first-run errors.
