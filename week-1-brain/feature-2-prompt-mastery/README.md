# Feature 2: Prompt Mastery

**Week 1 · Phase: Brain**

---

## What You'll Build

Feature 1 gave your assistant a voice. Feature 2 gives it *structure*. You'll write a system prompt that instructs the model to return a JSON object instead of free text — an object that classifies the user's intent, answers the question, and estimates how confident it is. The UI will render this as a visual response card with a colored badge for intent and a confidence meter.

This is one of the most important skills in AI engineering: the ability to design prompts that produce **reliably parseable, predictable output** from a model that is fundamentally a text predictor.

---

## Concepts Covered

| Term | Where to look |
|------|--------------|
| Structured output / JSON mode | [GLOSSARY.md — JSON](../../../GLOSSARY.md#json-javascript-object-notation) |
| System prompt engineering | [GLOSSARY.md — System Prompt](../../../GLOSSARY.md#system-prompt) |
| Temperature (set low for consistency) | [GLOSSARY.md — Temperature](../../../GLOSSARY.md#temperature) |
| Pydantic validation | `shared/models.py` — `StructuredResponse` |
| Intent classification | This README |
| Token efficiency | [GLOSSARY.md — Token](../../../GLOSSARY.md#token) |

---

## How to Run It

> Prerequisites: completed [SETUP.md](../../../SETUP.md) and have Feature 1 working.

1. Navigate to the starter folder:

```bash
cd week-1-brain/feature-2-prompt-mastery/starter
```

2. Start the server:

```bash
uvicorn main:app --reload --port 8000
```

3. Open `http://localhost:8000` — the chat UI now has a **Structured Mode** toggle.

4. With Structured Mode **off**, behavior is identical to Feature 1.

5. With Structured Mode **on**, responses are rendered as cards — once you implement the endpoint.

---

## Your Task

Open `starter/main.py`. There are two TODO items:

- [ ] **Step 1** — Write `_STRUCTURED_SYSTEM_PROMPT`. This is the hardest and most instructive part. Your prompt must:
  - Tell the model to return ONLY a JSON object with fields: `intent`, `answer`, `confidence`, `sources_needed`
  - Define each intent value clearly (`general_question`, `domain_question`, `action_request`, `unclear`)
  - Give confidence guidelines so the model uses the full 0–1 range meaningfully
  - Replace `[YOUR_DOMAIN]` with your actual domain
  - Fit in a paragraph or two — shorter, clearer prompts win

- [ ] **Step 2** — Implement the body of `chat_structured()`: `json.loads()` the result, construct a `StructuredResponse`, and add a `try/except` fallback for parse errors

- [ ] **Test with 3 query types** — try one of each:
  1. A general knowledge question: *"What is the capital of France?"*
  2. A domain-specific question: *"Do you carry hiking boots in size 12?"* (or your domain equivalent)
  3. An action request: *"Can you book me an appointment for Tuesday?"*

- [ ] **Observe** — does the model classify them correctly? What is the confidence for each? Does the `sources_needed` flag fire when you'd expect it to?

- [ ] **Iterate on the prompt** — if classifications are wrong or confidence numbers look off, adjust `_STRUCTURED_SYSTEM_PROMPT` and re-test. This iteration loop is the core skill of prompt engineering.

---

## Stretch Challenges

1. **Add a `follow_up_question` field** to `StructuredResponse` — the model generates one suggested follow-up the user could ask. Update the UI card to show it.
2. **Test with a very bad system prompt** — remove the JSON instructions entirely and see what happens to the parse fallback. This demonstrates why the fallback matters.
3. **Compare temperatures** — run the same query with `temperature=0.0` vs `temperature=0.9`. Which produces more stable JSON? Why?
4. **Multilingual test** — ask the same question in two languages. Does the intent classification still work?

---

## What's Next

**Feature 3** adds conversation memory — the assistant will remember what was said earlier in the session, so you can ask follow-up questions without repeating context.

→ See [resource/prompt-engineering-workbook.md](resource/prompt-engineering-workbook.md) (Resource 2) for 10 prompt improvement exercises, including two fully worked examples.
