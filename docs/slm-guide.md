# Running the Course on a Local SLM

**AI Engineering Bootcamp · BlockseBlock**

This guide is for students who want to run the entire course — or as much of it as possible — on a local Small Language Model (SLM) via Ollama, without sending data to a cloud provider.

---

## What Is an SLM?

An SLM (Small Language Model) is a compact AI model that runs entirely on your own laptop. No internet connection, no API key, no per-token cost. Examples used in this course: Phi-3 Mini, Gemma 2B, Mistral 7B, Llama 3.1 8B, Qwen2.5 7B.

The trade-off: SLMs are less capable than frontier cloud LLMs (GPT-4o, Claude 3.5, etc.) — they may struggle with very complex reasoning, long documents, or precise instruction-following. For learning the engineering patterns in this course, they work well for Features 1–9.

---

## Setup

1. Install Ollama from [https://ollama.com](https://ollama.com)
2. Run `ollama serve` (or it starts automatically on Mac after install)
3. Pull a model: `ollama pull llama3.1` (see recommendations below)
4. Set in `.env`:
   ```
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=llama3.1
   ```

---

## Recommended SLMs by Feature Compatibility

| Model | Pull Command | RAM Needed | F1-3 Chat | F4-6 RAG | F7-9 Agents | F10 Voice | Notes |
|-------|-------------|-----------|-----------|----------|-------------|-----------|-------|
| **Phi-3 Mini** (3.8B) | `ollama pull phi3:mini` | 4 GB | ✅ | ✅ | ⚠️ | ❌ | Best for low-spec laptops; strong at structured output and code |
| **Gemma 2B** | `ollama pull gemma:2b` | 4 GB | ✅ | ✅ | ⚠️ | ❌ | Google's smallest model; good general chat |
| **Mistral 7B** | `ollama pull mistral` | 8 GB | ✅ | ✅ | ✅ | ❌ | Excellent balance of speed and quality; strong tool calling |
| **Llama 3.1 8B** | `ollama pull llama3.1` | 8 GB | ✅ | ✅ | ✅ | ❌ | Best overall quality among SLMs; recommended default |
| **Qwen2.5 7B** | `ollama pull qwen2.5` | 8 GB | ✅ | ✅ | ✅ | ❌ | Strong at JSON/structured output; ideal for Features 2 and 6 |

**Key:** ✅ Works well · ⚠️ Works but may be unreliable · ❌ Not supported

---

## Feature Compatibility Details

### Features 1–3: Chat + Memory ✅ Fully offline

All three features work without internet. The session store is in-memory (no cloud), and call_llm() routes to your local Ollama model.

**JSON Mode caveat (Feature 2 + Feature 3):** Not all SLMs support `response_format={"type": "json_object"}` reliably. The OllamaProvider logs a warning and falls back to plain text if the model doesn't support it — Feature 2's `try/except` around `json.loads()` handles this gracefully. Use `llama3.1`, `qwen2.5`, or `mistral` for best JSON mode support.

### Features 4–6: Document Upload + RAG ✅ Fully offline

Document chunking and vector search are local (ChromaDB). Embeddings require an embeddings model — for fully offline use, set:
```
EMBEDDING_MODEL=nomic-embed-text
```
And pull the embedding model: `ollama pull nomic-embed-text`

If you're OK with one cloud call for embeddings: `text-embedding-3-small` (OpenAI) is cheap (~$0.0001 per document) and reliable.

### Features 7–9: Tool Calling + Agents ⚠️ Depends on model

Tool calling requires a model that supports Ollama's native function calling API. Recommended: `llama3.1`, `mistral`, `qwen2.5`. Older models or smaller models (phi3:mini, gemma:2b) may not follow tool schemas reliably.

If agents behave unpredictably with a local model, switch to `qwen2.5` first, then `llama3.1`. Cloud providers (Groq, OpenAI) will be more reliable for complex multi-step agents.

### Feature 10: Voice (STT + TTS) ❌ Requires cloud STT/TTS

Ollama does not include speech-to-text or text-to-speech APIs. For Feature 10 voice features, set a separate voice provider while keeping your chat model local:

```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
VOICE_PROVIDER=groq         # Groq STT is free — whisper-large-v3
STT_MODEL=whisper-large-v3
# For TTS (text-to-speech), you'll need VOICE_PROVIDER=openai instead
```

This means chat is local and free; only voice uses a cloud API.

### Features 11–12: Docker + Production Polish ✅ Fully offline

Containerization and rate limiting work regardless of provider.

---

## Context Window Comparison

SLMs have smaller context windows than frontier models. This affects Feature 3 (conversation history) and Features 4-6 (document retrieval).

| Model | Context Window | Effect on Course |
|-------|---------------|-----------------|
| Phi-3 Mini | 4,096 tokens | Keep sessions short; use CONTEXT_WINDOW_SIZE=8 in Feature 3 |
| Gemma 2B | 8,192 tokens | Standard CONTEXT_WINDOW_SIZE=20 is fine |
| Mistral 7B | 8,192 tokens | Standard settings work |
| Llama 3.1 8B | 128,000 tokens | Full context — no limitations |
| Qwen2.5 7B | 128,000 tokens | Full context — no limitations |

For Phi-3 Mini, reduce `CONTEXT_WINDOW_SIZE` in `solution/main.py` from 20 to 8 to avoid prompt overflow errors.

---

## Troubleshooting

**"Connection refused" / "Can't reach Ollama"**
→ Run `ollama serve` in a terminal first. On Mac, Ollama may start automatically after install — check the menu bar icon.

**Responses are very slow**
→ Try a smaller model (`phi3:mini` or `gemma:2b`). SLMs run on CPU if you don't have a supported GPU — expect 5-15 tokens/second on CPU vs 50-100+ on a modern GPU.

**JSON mode not working (Feature 2)**
→ Switch to `qwen2.5` or `llama3.1`. The fallback (intent="unclear") will fire for models that ignore JSON mode — this is expected behaviour, not a crash.

**Tool calling not working (Features 7-9)**
→ Switch to `llama3.1` or `qwen2.5`. Not all models support function calling.

---

## Running Fully Offline: Checklist

- [ ] `ollama pull llama3.1` (or your preferred model)
- [ ] `ollama pull nomic-embed-text` (for local embeddings — Feature 5)
- [ ] Set `LLM_PROVIDER=ollama` in `.env`
- [ ] Set `EMBEDDING_MODEL=nomic-embed-text` in `.env`
- [ ] Set `VOICE_PROVIDER=groq` + `GROQ_API_KEY=...` when you reach Feature 10 STT
  (or skip voice entirely — Features 1-9 are fully offline)
- [ ] For Feature 2 JSON mode: use `OLLAMA_MODEL=qwen2.5` or `llama3.1`
- [ ] For Features 7-9 agents: use `OLLAMA_MODEL=llama3.1` or `mistral`
