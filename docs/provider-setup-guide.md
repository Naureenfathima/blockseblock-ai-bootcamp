# Provider Setup Guide

**AI Engineering Bootcamp · BlockseBlock**

This course supports four AI providers out of the box. You only need to set up **one** — whichever works best for your situation.

---

## Quick Comparison

| Provider | What you need | Cost | Voice (Feature 10) | Tool Calling / Agents (Features 7-9) |
|----------|---------------|------|--------------------|--------------------------------------|
| **OpenAI** | API key | Pay per use | Yes (built-in) | Yes (excellent) |
| **Anthropic** | API key | Pay per use | No — set `VOICE_PROVIDER=openai` | Yes (excellent) |
| **Cohere** | API key | Free tier available | No — set `VOICE_PROVIDER=openai` | Yes (good) |
| **Ollama** | Local install — no key | Free | No — set `VOICE_PROVIDER=openai` | Depends on model (see below) |

---

## Which Should I Pick?

**Want the smoothest experience across all 12 features, including voice and agents?**  
→ Use **OpenAI** or **Anthropic**. If you pick Anthropic, add `VOICE_PROVIDER=openai` to your `.env` for Feature 10.

**Want it completely free and private, and have a decent computer (16 GB RAM+)?**  
→ Use **Ollama** with `llama3.1` or `qwen2.5`. Note: Feature 10 voice features require a speech-capable provider, so you'll add `VOICE_PROVIDER=openai` when you reach Week 4.

**Already have a Cohere key and mainly care about chat and RAG (Features 1-6)?**  
→ Use **Cohere**, with `VOICE_PROVIDER=openai` added when you reach Feature 10.

---

## Provider Setup Instructions

### OpenAI

1. Go to [platform.openai.com](https://platform.openai.com) and sign up or log in.
2. Navigate to **API Keys** and create a new key.
3. Add these lines to your `.env`:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

`gpt-4o-mini` is a good starting point — it's fast and cost-effective. Switch to `gpt-4o` if you want more capable reasoning.

---

### Anthropic

1. Go to [console.anthropic.com](https://console.anthropic.com) and sign up or log in.
2. Navigate to **API Keys** and create a new key.
3. Add these lines to your `.env`:

```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-6
```

Because Anthropic doesn't provide speech APIs, add this when you reach Feature 10:

```
VOICE_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
```

---

### Cohere

1. Go to [dashboard.cohere.com](https://dashboard.cohere.com) and sign up or log in.
2. Navigate to **API Keys** and copy your trial or production key.
3. Add these lines to your `.env`:

```
LLM_PROVIDER=cohere
COHERE_API_KEY=your-cohere-key-here
COHERE_MODEL=command-r-plus
```

Cohere's trial key works for Features 1-9. For Feature 10 voice, add:

```
VOICE_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
```

---

### Ollama (Local — Free)

Ollama runs AI models directly on your computer. No API key, no cost, no data leaving your machine.

**Requirements:** 16 GB RAM recommended (8 GB minimum with smaller models).

1. Install Ollama from [ollama.com](https://ollama.com). Download the installer for your OS.

2. Open a terminal and pull a model:

```bash
ollama pull llama3.1
```

This downloads the model (roughly 4-5 GB). One-time download.

3. Start the Ollama server (keep this terminal open):

```bash
ollama serve
```

4. Add these lines to your `.env`:

```
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

5. For Feature 10 voice features, you'll need a speech-capable provider:

```
VOICE_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
```

**Recommended models for each feature set:**

| Feature set | Recommended model |
|-------------|------------------|
| Features 1-6 (chat, RAG) | `llama3.1`, `mistral`, `phi3` |
| Features 7-9 (tool calling, agents) | `llama3.1`, `qwen2.5`, `mistral-nemo` |
| Features 10-12 (voice, production) | Use `VOICE_PROVIDER=openai` for speech |

---

### Custom OpenAI-Compatible Endpoint

If your provider exposes an OpenAI-compatible `/v1/chat/completions` endpoint (e.g. Azure OpenAI, Together AI, Groq, Fireworks):

```
LLM_PROVIDER=custom
CUSTOM_BASE_URL=https://your-provider.com/v1
CUSTOM_API_KEY=your-key-here
CUSTOM_MODEL=your-model-name
```

---

## Verifying Your Setup

After editing `.env`, start the server from any feature's `solution/` folder:

```bash
uvicorn main:app --reload --port 8000
```

Watch the terminal output. If there's a problem with your configuration (missing key, Ollama not running, etc.), you'll see a clear error message before the server finishes starting.

If the server starts cleanly, open `http://localhost:8000/api/provider-info` — you should see a JSON response confirming your active provider and model.
