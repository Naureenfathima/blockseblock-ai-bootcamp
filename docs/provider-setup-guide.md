# Provider Setup Guide

**AI Engineering Bootcamp · BlockseBlock**

This course supports nine AI providers. You only need to set up **one** — whichever works best for your situation.

---

## Quick Comparison

| Provider | What you need | Free tier? | STT voice | TTS voice | Agents (F7-9) | Recommended for |
|----------|---------------|-----------|-----------|-----------|---------------|-----------------|
| **Groq** | API key | Yes ✅ | Yes ✅ | No ❌ | Yes ✅ | Beginners — fast, free, no credit card |
| **OpenAI** | API key | No | Yes ✅ | Yes ✅ | Yes ✅ | Smoothest all-12-features experience |
| **Anthropic** | API key | No | No ❌ | No ❌ | Yes ✅ | High-quality reasoning, privacy-focused |
| **Cohere** | API key | Yes ✅ | No ❌ | No ❌ | Yes ✅ | Features 1-6, chat and RAG |
| **Ollama** | Local install | Free ✅ | No ❌ | No ❌ | Model-dependent | Fully offline, privacy-sensitive use |
| **Azure OpenAI** | Azure account | No | No ❌ | No ❌ | Yes ✅ | Enterprise on Microsoft/Azure |
| **AWS Bedrock** | AWS account | No | No ❌ | No ❌ | Yes ✅ | Enterprise on AWS |
| **GCP Vertex AI** | GCP account | No | No ❌ | No ❌ | Yes ✅ | Enterprise on Google Cloud |
| **Custom** | Any OpenAI-compatible URL | Varies | Varies | Varies | Varies | Together AI, Fireworks, vLLM, etc. |

---

## Which Should I Pick?

**Want everything free + fast + no credit card? (Recommended for most students)**  
→ Use **Groq**. Free tier at [console.groq.com](https://console.groq.com), no credit card needed. Supports chat, RAG, agents (Features 1-9), and STT voice (Feature 10). For TTS only, add `VOICE_PROVIDER=openai`.

**Want it completely free and private, running on your own computer?**  
→ Use **Ollama** with `llama3.1` or `qwen2.5`. No API key, no internet. For Feature 10 voice, add `VOICE_PROVIDER=groq` (free STT) or `VOICE_PROVIDER=openai`.  
→ See [docs/slm-guide.md](slm-guide.md) for model recommendations by feature.

**Want the smoothest experience across all 12 features including TTS?**  
→ Use **OpenAI** or **Anthropic**. If you pick Anthropic, add `VOICE_PROVIDER=openai` for Feature 10 TTS.

**Already have a Cohere key and mainly care about chat and RAG (Features 1-6)?**  
→ Use **Cohere**, with `VOICE_PROVIDER=groq` for Feature 10 STT.

**Enterprise / on a cloud platform?**  
→ Azure (on Microsoft), Bedrock (on AWS), or Vertex (on GCP). Same code, different `.env`.

---

## Provider Setup Instructions

### Groq ⭐ Recommended for Beginners

Groq runs open-weight models (Llama, Mistral, Gemma) on custom LPU hardware — very fast inference, generous free tier, no credit card required.

1. Go to [console.groq.com](https://console.groq.com) and sign up (takes 2 minutes).
2. Navigate to **API Keys** and create a new key.
3. Add these lines to your `.env`:

```
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

**Groq model recommendations:**

| Model | Best for | Speed |
|-------|----------|-------|
| `llama-3.3-70b-versatile` | Best quality, agents (F7-9) | Fast |
| `llama-3.1-8b-instant` | Chat/RAG (F1-6), voice latency (F10) | Very fast |
| `mixtral-8x7b-32768` | Long documents, extended history (F3) | Fast |
| `gemma2-9b-it` | Structured output (F2) | Fast |

For Feature 10 voice (STT), Groq also works as the voice provider:

```
VOICE_PROVIDER=groq
STT_MODEL=whisper-large-v3
# For TTS, set VOICE_PROVIDER=openai separately
```

> **Groq callout:** Groq's free tier is genuinely useful for this entire course — generous rate limits, fast responses, and Whisper STT included. Set `LLM_PROVIDER=groq` and `VOICE_PROVIDER=groq` and Features 1-10 (except TTS) work out of the box.

---

### OpenAI

1. Go to [platform.openai.com](https://platform.openai.com) and sign up or log in.
2. Navigate to **API Keys** and create a new key.
3. Add these lines to your `.env`:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

`gpt-4o-mini` is a good starting point — fast and cost-effective. Switch to `gpt-4o` for more capable reasoning.

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
VOICE_PROVIDER=groq    # free STT
GROQ_API_KEY=gsk_your-key-here
# or VOICE_PROVIDER=openai for both STT and TTS
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

For Feature 10 voice, add:

```
VOICE_PROVIDER=groq
GROQ_API_KEY=gsk_your-key-here
```

---

### Ollama (Local — Free)

Ollama runs AI models directly on your computer. No API key, no cost, no data leaving your machine. See [docs/slm-guide.md](slm-guide.md) for model recommendations and feature compatibility details.

**Requirements:** 8 GB RAM minimum (16 GB recommended for larger models).

1. Install Ollama from [ollama.com](https://ollama.com).
2. Pull a model:

```bash
ollama pull llama3.1
```

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

5. For Feature 10 voice:

```
VOICE_PROVIDER=groq
GROQ_API_KEY=gsk_your-key-here
STT_MODEL=whisper-large-v3
```

---

### Azure OpenAI

Azure OpenAI = the same models (GPT-4o, etc.) running inside Microsoft's data centers. Required for many enterprise customers due to data residency and compliance.

1. In the [Azure Portal](https://portal.azure.com), create an Azure OpenAI resource.
2. In Azure AI Studio, create a deployment of your chosen model.
3. Add these lines to your `.env`:

```
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-01
```

For Feature 10 voice, add `VOICE_PROVIDER=openai` with a standard OpenAI key.

---

### AWS Bedrock

AWS Bedrock = Claude, Llama, Mistral, and others through your existing AWS account. Everything stays inside your AWS VPC.

1. In the AWS Console, navigate to **Amazon Bedrock** and enable model access for your chosen model.
2. Create an IAM user with `AmazonBedrockFullAccess` (or a scoped policy) and note its access keys.
3. Add these lines to your `.env`:

```
LLM_PROVIDER=bedrock
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

Requires `boto3`: `pip install boto3`

Example model IDs:
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `meta.llama3-8b-instruct-v1:0`
- `mistral.mistral-7b-instruct-v0:2`

---

### GCP Vertex AI

GCP Vertex AI = Gemini and open-weight models inside Google Cloud. Preferred when the rest of your stack is already on GCP.

1. Enable the **Vertex AI API** in your [GCP project](https://console.cloud.google.com).
2. Authenticate locally: `gcloud auth application-default login`
3. Add these lines to your `.env`:

```
LLM_PROVIDER=vertex
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
VERTEX_MODEL=google/gemini-2.0-flash-001
```

Requires `google-auth`: `pip install google-auth`

---

### Custom OpenAI-Compatible Endpoint

For Together AI, Fireworks, Mistral, local vLLM servers, or any other provider with an OpenAI-compatible API:

```
LLM_PROVIDER=custom
CUSTOM_BASE_URL=https://your-provider.com/v1
CUSTOM_API_KEY=your-key-here
CUSTOM_MODEL=your-model-name
```

---

## Alternative Retrieval: PageIndex

PageIndex is **not an LLM provider** — it's a different retrieval architecture used in Feature 6's Smart Router alongside your chosen provider.

| | RAG (Features 4-6) | PageIndex |
|---|---|---|
| **How it retrieves** | Vector similarity search | LLM reasoning over a hierarchical tree index |
| **Chunking required** | Yes | No |
| **Vector DB required** | Yes | No |
| **Best for** | General semantic queries, many documents | Long professional docs (financial, legal, technical) |
| **FinanceBench accuracy** | Significantly lower | 98.7% |

**When to consider PageIndex instead of standard RAG:**
- Financial reports, legal filings, regulatory documents, technical manuals (50-500 pages)
- Your RAG pipeline keeps returning wrong answers despite tuning chunk size and overlap
- The document has complex internal structure — cross-references, defined terms, section hierarchies

**Setup (Feature 6):**
```bash
pip install -r requirements.txt  # from github.com/VectifyAI/PageIndex
python run_pageindex.py --pdf_path your_doc.pdf   # builds tree JSON
# Feature 6 Smart Router routes: professional docs → PageIndex, general queries → vector RAG
```

Source: [github.com/VectifyAI/PageIndex](https://github.com/VectifyAI/PageIndex) (MIT licence). Cloud service + MCP server at [pageindex.ai](https://pageindex.ai).

---

## Verifying Your Setup

After editing `.env`, start the server from any feature's `solution/` folder:

```bash
uvicorn main:app --reload --port 8000
```

Watch the terminal output. If there's a problem with your configuration (missing key, Ollama not running, etc.), you'll see a clear error message before the server finishes starting.

If the server starts cleanly, open `http://localhost:8000/api/provider-info` — you'll see a JSON response confirming your active provider and model.
