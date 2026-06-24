# Feature 4: Feed the Brain

**Week 2 · Phase: Knowledge**

---

## What You'll Build

Your assistant can chat and remember conversations — but it only knows what you put in the system prompt. Feature 4 fixes that. You'll build a **document ingestion pipeline**: upload a file, extract its text, split it into chunks using a selectable strategy, and store them. The Documents tab shows each file's status, strategy, chunk count, and lets you inspect the actual chunks.

This is the data-loading half of RAG. Feature 5 adds the retrieval half.

---

## The Four Architectures: RAG, CAG, KAG, and PageIndex

Before building chunking, you need to understand there are **four fundamentally different approaches** to giving an LLM access to external knowledge. Feature 4 begins the RAG path, but each approach has a different best-fit domain:

### 1. RAG — Retrieval-Augmented Generation *(what this course builds, F4-F6)*
Documents → chunk → embed → vector DB → retrieve relevant chunks at query time → inject into prompt.

**Strength:** Scales to large document libraries. Cost stays roughly constant per query regardless of total document volume.  
**Core limitation:** "Vibe retrieval" — similarity ≠ relevance. The most similar passage is not always the most relevant one.  
**Best for:** Many documents, semantic questions, production scale.

### 2. CAG — Cache-Augmented Generation *(skip chunking entirely)*
Load **all** document text into one system prompt. The model's KV cache is pre-computed once and reused across queries — no retrieval, no vector DB, no chunking decisions.

**Strength:** Zero retrieval errors. The model reads everything and can reason across all documents simultaneously.  
**Core limitation:** Breaks down as document volume grows past the context window. Cost per query is high.  
**Best for:** < ~50 pages, stable documents that rarely change, situations where missing a chunk is unacceptable.

```python
# CAG pattern (conceptual — documented in shared/ingestion.py):
all_text = "\n\n".join(extract_text(b, f) for b, f in documents)
system_prompt = f"Here is all relevant knowledge:\n{all_text}\n\nAnswer..."
```

### 3. KAG — Knowledge-Augmented Generation *(introduced in Feature 6)*
Extract entities and relationships from documents into a **knowledge graph** (subject → predicate → object triples), then use graph traversal + LLM reasoning for retrieval instead of vector similarity.

**Strength:** Precise for relational and factual queries ("what connects Policy A to Regulation B?").  
**Core limitation:** Requires LLM-based extraction step at ingestion time and a graph database.  
**Best for:** Relational/factual queries, compliance documents, anything where multi-hop reasoning matters.  
**Where we add this:** Feature 6's Smart Router introduces a KAG path alongside standard RAG routing.

### 4. PageIndex — Vectorless, Reasoning-based RAG *(VectifyAI, MIT licence)*
By [VectifyAI](https://github.com/VectifyAI/PageIndex) — a fundamentally different approach:

1. **Build a hierarchical tree index** — like a smart table of contents optimised for LLMs. Each tree node has a title, a page range, and an LLM-generated summary of what that section contains.
2. **Retrieve by reasoning over the tree** — an LLM agent navigates the tree structure to find the most relevant section, simulating how a human expert flips through a complex report. No vector similarity used at all.

**The key insight from the PageIndex paper:** *"similarity ≠ relevance."* Vector RAG returns semantically similar passages. PageIndex returns the passages an expert would find.

**Results:** 98.7% accuracy on FinanceBench vs significantly lower for traditional vector RAG systems.

**Best for:** Long professional documents — financial reports, legal filings, academic papers, regulatory documents, technical manuals — where multi-step reasoning is needed to find the right section.

```bash
# Integration (after Feature 5 you'll have the retrieval context to add this):
pip install -r requirements.txt  # from github.com/VectifyAI/PageIndex
python run_pageindex.py --pdf_path your_doc.pdf  # generates a tree JSON
# In Feature 6's Smart Router: route professional-doc queries to PageIndex,
# general queries to vector RAG
```

Cloud service + MCP server: pageindex.ai

---

## Architecture Decision Guide

| | RAG | CAG | KAG | PageIndex |
|---|---|---|---|---|
| **Document volume** | Many | Few (<50 pages) | Any | Long single docs |
| **Query type** | Semantic | Any | Relational/factual | Complex/reasoning |
| **Retrieval errors** | Possible | None | None | Minimal |
| **Setup complexity** | Medium | Low | High | Medium |
| **Scales with doc count** | Yes | No | Yes | Yes |
| **Needs vector DB** | Yes | No | No | No |
| **Best domain** | General | Stable small sets | Policy/compliance | Finance/legal/technical |

> **Quick decision rule:**
> - < 20 pages, stable, zero errors required → **CAG**
> - "How does X relate to Y?" → **KAG**
> - Long financial/legal/technical doc, chunking produces wrong answers → **PageIndex**
> - Everything else → **RAG** (what we build)

---

## Concepts Covered

| Term | Where to look |
|------|--------------|
| RAG | GLOSSARY.md + this README |
| CAG | This README + `shared/ingestion.py` CAG comment block |
| KAG | This README (brief) + Feature 6 advanced section |
| PageIndex | This README + `shared/ingestion.py` PAGEINDEX_NOTE |
| Text extraction | `shared/ingestion.py` → `extract_text()` |
| Chunking strategies | `shared/ingestion.py` + Resource 4 |
| Chunk overlap | `shared/ingestion.py` → `chunk_text()` docstring |
| Document store | `shared/document_store.py` |
| Document / Chunk models | `shared/models.py` |

---

## Two Selectable Chunking Strategies

| Strategy | How it splits | Best for |
|----------|--------------|----------|
| **sentence** (default) | Sentence boundaries; group ~500 chars; carry overlap | Most documents |
| **paragraph** | Double newlines; fallback to sentence split for long paragraphs | Formal structured docs (policies, manuals, legal) |

Select the strategy in the UI dropdown before uploading, or pass `strategy=paragraph` as a form field.

---

## How to Run It

```bash
cd week-2-knowledge/feature-4-feed-the-brain/starter
uvicorn main:app --reload --port 8000
```

Features 1–3 work immediately. Upload endpoints return 501 until you complete `ingestion.py`. Open `http://localhost:8000` and click the **Documents** tab.

---

## Your Task

**Step 1–3:** Open `starter/ingestion.py` → implement `extract_text()`:

- [ ] `.txt` — decode bytes as UTF-8
- [ ] `.pdf` — use `pypdf.PdfReader`, join pages with `"\n"`
- [ ] `.docx` — use `docx.Document`, join non-empty paragraph texts

**Step 4:** Implement the sentence accumulation loop in `chunk_text()`:

- [ ] If current is non-empty and adding the sentence exceeds chunk_size: emit chunk, build overlap tail, reset current
- [ ] Append each sentence, update current_len

**Step 5:** Read the reference implementations:

- [ ] `chunk_by_paragraph()` — compare how it handles boundaries differently
- [ ] `chunk_by_page()` — understand per-page chunking and how metadata flows
- [ ] **CAG PATTERN** comment — understand when you'd skip this module entirely
- [ ] **PAGEINDEX NOTE** comment — understand when neither chunking nor vectors help

**Step 6:** Compare strategies in the UI:

- [ ] Upload the same document with **sentence** then **paragraph** strategy — compare chunk counts
- [ ] Note any chunks that look "badly cut" (see Resource 4 for tuning)
- [ ] Consider: is this a domain (financial/legal) where PageIndex would outperform chunking?

---

## Key Files

| File | What it does |
|------|-------------|
| `starter/ingestion.py` | Your work: `extract_text()` + `chunk_text()` |
| `shared/ingestion.py` | Complete solution + architecture docs |
| `shared/document_store.py` | In-memory Document + Chunk storage |
| `shared/models.py` | `Document` (with `chunking_strategy`) + `Chunk` models |
| `solution/main.py` | Complete Feature 4 server |
| `resource/chunking-strategies-guide.md` | Resource 4: all 4 architectures + strategies compared |

---

## What's Next

Feature 5 adds **vector embeddings** and semantic search — retrieving the right chunks at query time. Your assistant will be able to answer questions from your uploaded documents.

For long professional documents where chunking-based RAG consistently produces wrong answers, Feature 6's Smart Router is where we introduce PageIndex as an alternative retrieval path.
