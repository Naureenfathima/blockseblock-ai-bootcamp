# Resource 4: Chunking Strategies Guide

**Feature 4 · AI Engineering Bootcamp · BlockseBlock**

Before you can search a document, you have to understand the design space. This guide covers **four architectures** for giving an LLM access to external knowledge, then dives into the three chunking strategies used within the RAG path.

---

## Section 1: The Four Architectures

### 1. RAG — Retrieval-Augmented Generation
**What it does:** Documents → chunk → embed → vector DB. At query time, compute similarity between the user's query embedding and all chunk embeddings, retrieve the top-k matches, inject them into the prompt.

**Core limitation:** "Vibe retrieval" — vector similarity returns semantically similar text, not necessarily the most relevant text. A passage about "risk management strategy" might score high for a query about "strategic risk" even if it's about supply chain, not financial risk.

**Best for:** General semantic queries across large document libraries. The industry default.

---

### 2. CAG — Cache-Augmented Generation
**What it does:** Skip chunking entirely. Concatenate all document text into one large system prompt. A large-context model processes it all and caches the KV (key-value) representation — subsequent queries reuse the cache without re-reading the documents.

**The trade-off:**

| | RAG | CAG |
|--|--|--|
| Document volume | Scales to hundreds | Breaks past ~50-100 pages |
| Retrieval errors | Possible | None |
| Cost per query | Constant | Grows with doc volume |
| Setup | Complex (vector DB) | Trivial (concatenate + prompt) |

**Pattern (documented in `shared/ingestion.py`):**
```python
all_text = "\n\n---\n\n".join(extract_text(b, f) for b, f in documents)
system_prompt = f"Here is all relevant knowledge:\n{all_text}\n\nAnswer using only this."
```

**When CAG beats RAG:** < 50 pages total, documents rarely change, missing any chunk is unacceptable (medical, legal), using GPT-4o (128K tokens) or Gemini 1.5 Pro (1M tokens).

---

### 3. KAG — Knowledge-Augmented Generation
**What it does:** Extract structured knowledge (entities + relationships) from documents into a knowledge graph during ingestion. At query time, traverse the graph using LLM reasoning rather than vector similarity.

**Example triples extracted from text:**
```
"Amazon deforestation" → caused_by → "agricultural expansion"
"Amazon deforestation" → caused_by → "logging"
"20-25% cleared"       → triggers   → "ecosystem tipping point"
```

**Why it beats RAG for relational queries:**
> "What activities drive the tipping point risk for the Amazon?"

RAG might retrieve passages about "risk" generally. KAG traverses: `tipping_point ← triggered_by ← deforestation ← caused_by → [agriculture, logging]` and returns the exact answer.

**Cost:** Requires LLM extraction at ingestion time and a graph database (Neo4j, NetworkX). Introduced in Feature 6's Smart Router.

---

### 4. PageIndex — Vectorless, Reasoning-based RAG *(VectifyAI)*
**Source:** github.com/VectifyAI/PageIndex (MIT licence, 30k+ stars)

**What it does:**
1. Builds a **hierarchical tree index** — like a smart table of contents optimised for LLMs. Each tree node contains: title, page range, LLM-generated summary of that section.
2. Retrieves by **LLM reasoning over the tree** — an LLM agent navigates the tree the way a human expert flips through a complex document. No embedding. No similarity. No chunk boundaries.

**The key insight:** *"Similarity ≠ relevance."*
A vector search for "net revenue" returns all passages mentioning revenue. A PageIndex tree search asks "which section of this financial report discusses net revenue for Q3?" and navigates directly to it.

**Results on FinanceBench:** PageIndex achieved 98.7% accuracy — significantly higher than traditional vector RAG systems on financial document Q&A.

**No chunking means no chunking errors:** documents like legal contracts, financial statements, and technical manuals have complex internal structures (cross-references, defined terms, section hierarchies) that naive chunking disrupts.

**When to use PageIndex instead of RAG:**
- Long professional documents (50-500 pages)
- Financial reports, legal filings, regulatory documents, technical manuals
- Multi-step reasoning needed to navigate to the right section
- Vector RAG keeps returning wrong answers despite tuning

**Integration in Feature 6:**
```bash
pip install -r requirements.txt  # from github.com/VectifyAI/PageIndex
python run_pageindex.py --pdf_path your_doc.pdf  # builds tree JSON
# Feature 6 Smart Router: route professional docs → PageIndex
#                          general queries         → vector RAG
```

Cloud service and MCP server: pageindex.ai

---

## Section 2: Three Chunking Strategies for RAG

When you've decided to use RAG, chunking quality determines retrieval quality. The same document, chunked differently, produces dramatically different retrieval results. These examples all use the same sample paragraph.

**Sample text:**
> The Amazon rainforest covers approximately 5.5 million square kilometres. It is home to an estimated 10% of all species on Earth. Deforestation has accelerated in recent decades, driven by agricultural expansion and logging. Scientists warn that if 20–25% of the forest is cleared, the ecosystem may cross a tipping point from which it cannot recover. Conservation efforts, including indigenous land protections and international agreements, aim to prevent this outcome.

---

### Strategy 1: Fixed-Size Naive (baseline — don't use)

**How it works:** Count characters. Every N characters, cut — regardless of word or sentence boundaries.

**Example (chunk_size=120):**
```
Chunk 0: "The Amazon rainforest covers approximately 5.5 million square kilometres. It is home to an estimated 10% of all spec"
Chunk 1: "ies on Earth. Deforestation has accelerated in recent decades..."
```

`spec / ies` are split across chunks. No embedding model will connect them.

**Only use as:** a measurement baseline when benchmarking other strategies.

---

### Strategy 2: Sentence-Aware Fixed-Size *(default — what we build)*

**How it works:** Split on sentence-ending punctuation (`. ! ?`), group sentences until ~`chunk_size` chars, carry ~`overlap` chars from the tail of the previous chunk into the next.

**Example (chunk_size=180, overlap=50):**
```
Chunk 0: "The Amazon rainforest covers approximately 5.5 million square kilometres.
          It is home to an estimated 10% of all species on Earth."
Chunk 1: "It is home to an estimated 10% of all species on Earth.
          Deforestation has accelerated in recent decades, driven by agricultural expansion and logging."
Chunk 2: "Scientists warn that if 20–25% of the forest is cleared,
          the ecosystem may cross a tipping point from which it cannot recover."
Chunk 3: "Conservation efforts, including indigenous land protections and international agreements,
          aim to prevent this outcome."
```

*(Chunk 1 starts with a sentence carried from Chunk 0 — that's the overlap.)*

**Never cuts mid-sentence. Works for any text format. The go-to default.**

---

### Strategy 3: Paragraph-Based

**How it works:** Split on double newlines (`\n\n`). Each paragraph becomes a chunk, or short paragraphs are grouped. Oversized paragraphs fall back to sentence-aware splitting.

**Best for:** Formal structured documents (policies, manuals, legal text, Markdown) where each paragraph already expresses one coherent idea. Breaks down for unstructured text (transcripts, raw OCR, emails).

**Advantage over sentence strategy:** paragraphs are written to be coherent units — the chunk boundaries align with human authorial intent, not just sentence count. This often means better retrieval relevance.

---

## Section 3: Choosing and Tuning

### Architecture first, chunking second

```
Is the document set small and stable (<50 pages)?
  Yes → try CAG first (one prompt, no retrieval errors)
  No  → continue

Are the queries relational/factual ("how does X connect to Y?")?
  Yes → KAG (knowledge graph, see Feature 6)
  No  → continue

Is this a long professional document (financial/legal/technical)?
  Yes → try PageIndex (github.com/VectifyAI/PageIndex)
  No  → continue

Use RAG with chunking (you're here):
  Formal structured text (policies, manuals) → paragraph strategy
  Everything else                             → sentence strategy (default)
```

### Overlap tuning

| Overlap | Effect | Good for |
|---------|--------|----------|
| 0 chars | Zero redundancy, maximum boundary loss | Very short sentences |
| 50 chars (default) | Low redundancy, handles most cases | General documents |
| 100–150 chars | Higher redundancy, robust for long sentences | Technical/legal docs |
| > 200 chars | Significant overlap — consider larger chunk_size instead | Rarely needed |

### Signs your chunks are wrong

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Question about X returns no results | X spans a chunk boundary | Increase overlap |
| All results come from one chunk | chunk_size too large | Reduce chunk_size |
| Many irrelevant results | chunk_size too small | Increase chunk_size |
| Correct answer exists but never retrieved | Strategy mismatch | Try paragraph; or consider PageIndex |

---

## Section 4: Hand Exercise

Chunk this paragraph using **two different strategies**. Write out your chunks and note where each strategy draws its boundaries.

> "Electric vehicles have reached cost parity with petrol cars in several markets. Battery technology continues to improve, with energy density doubling roughly every decade. However, charging infrastructure remains uneven — rural areas often have few or no public chargers. Governments have introduced incentives to accelerate adoption, including purchase subsidies and manufacturer mandates."

**Questions:**
1. Which chunks best answer *"Why is EV adoption slow in rural areas?"*
2. Which strategy produced the most complete chunk for that answer?
3. Is this a domain where PageIndex would outperform chunking-based RAG? Why or why not?
4. Under what conditions would CAG be the right choice for an EV industry knowledge base?

There is no single correct answer — this is the judgment call at the heart of knowledge system design.
