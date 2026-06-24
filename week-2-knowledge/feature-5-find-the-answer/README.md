# Feature 5: Find the Answer

**Week 2 · Phase: Knowledge**

---

## What You'll Build

Feature 4 built the ingestion half of RAG: documents → chunks → stored.
Feature 5 builds the retrieval half: question → embed → search → ranked results.

You'll implement `add_chunks()` and `search()` in `starter/vector_store.py`,
wiring your uploaded documents into a local ChromaDB vector database. The
"Ask My Documents" tab in the UI lets you run semantic searches and see the
similarity scores in real time.

---

## Architectural Context

In Feature 4 we introduced four approaches to giving an LLM external knowledge.
We chose RAG because it scales. Feature 5 builds RAG's retrieval layer — the
step that takes a question and finds the most relevant chunks.

**This is also the step PageIndex replaces entirely.**

| Approach | How retrieval works |
|---|---|
| **RAG (what we build)** | Question → embed → vector similarity search → top-k chunks |
| **PageIndex (VectifyAI)** | Question → LLM navigates hierarchical tree index → exact section |

We're building similarity-based retrieval here. It works well for most domains
and scales to large document libraries. The limitation flagged in Feature 4
still applies: **similarity ≠ relevance.** For professional long documents
(financial, legal, regulatory) where you find vector RAG consistently returning
wrong or partially-right answers — that's the signal to evaluate PageIndex as
an alternative retrieval approach.

---

## New Concepts

### Embeddings — text as coordinates

An embedding model converts text into a list of numbers (a vector). Similar
meanings produce vectors that are close together in this high-dimensional space.

```
"The policy requires annual renewal"    → [0.12, -0.87, 0.44, ...]
"Documents must be renewed every year"  → [0.13, -0.85, 0.41, ...]  ← close!
"Recipe for chocolate cake"             → [-0.71, 0.23, -0.58, ...] ← far
```

We don't look at these numbers directly. We just ask: which stored chunk
vectors are nearest to the question vector?

### Vector database — nearest-neighbor search

A regular database finds rows where `text = "exact phrase"`. A vector database
finds rows where `vector ≈ query_vector` — similarity in meaning space, not
exact text matching.

ChromaDB is a local vector database: no external service, no API key, stores
data on disk in `./data/vectordb`. Every uploaded document's chunks are
automatically embedded and indexed.

### Similarity score — and its limitation

When ChromaDB returns matches, it returns L2 distances. We convert to a
0.0–1.0 score:  `score = max(0.0, 1.0 - (distance / 2.0))`

Higher score = vectors closer together = more semantically similar.

**HONEST LIMITATIONS:**
The score is a similarity score, not a relevance score. A chunk can be
semantically similar to your question without actually answering it — and a
relevant chunk can score low if it uses different vocabulary than your question.

This is the core limitation of vector RAG. Feature 6 adds LLM-based
classification to compensate. PageIndex (Resource 4) replaces similarity
with reasoning for domains where this matters most.

### Framework bridge — LangChain equivalents

`shared/vector_store.py` IS what LangChain calls a `VectorStore`.

| This module | LangChain equivalent |
|---|---|
| `add_chunks(texts, metas)` | `vectorstore.add_texts(texts, metadatas)` |
| `search(query, top_k)` | `vectorstore.similarity_search_with_score(query, k)` |
| `1.0 - (distance / 2.0)` | What LangChain does internally when returning scores |
| ChromaDB PersistentClient | `Chroma(persist_directory=...)` |

Now you know what the abstraction is actually doing.

---

## Architecture Decision Guide

| | RAG | CAG | KAG | PageIndex |
|---|---|---|---|---|
| **Document volume** | Many | Few (<50 pages) | Any | Long single docs |
| **Query type** | Semantic | Any | Relational/factual | Complex/reasoning |
| **Retrieval errors** | Possible | None | None | Minimal |
| **Needs vector DB** | Yes | No | No | No |
| **Best domain** | General | Stable small sets | Policy/compliance | Finance/legal/technical |

---

## Key Files

| File | What it does |
|------|-------------|
| `starter/vector_store.py` | Your work: `add_chunks()` + `search()` |
| `shared/vector_store.py` | Complete solution |
| `shared/ingestion.py` | Text extraction + chunking (Feature 4) |
| `shared/document_store.py` | In-memory chunk storage |
| `shared/config.py` | `VECTOR_DB_PATH` setting |
| `solution/main.py` | Complete Feature 5 server |

---

## Your Task

**Step 1:** Implement `add_chunks()` in `starter/vector_store.py`:
- [ ] Call `collection.add(documents=..., metadatas=..., ids=...)` — one line

**Step 2:** Implement `search()` in `starter/vector_store.py`:
- [ ] Call `collection.query(query_texts=..., n_results=..., where=...)` — see the TODO
- [ ] Convert distance to score: `score = max(0.0, 1.0 - (distance / 2.0))`
- [ ] Build and return the list of result dicts

**Step 3:** Verify in the UI ("Ask My Documents" tab):
- [ ] Upload a domain document (Feature 4 must be working first)
- [ ] Ask a question that shares **no exact words** with the document — confirm semantic similarity still finds the relevant chunk
- [ ] Ask a nonsense question — note the low scores
- [ ] Ask a question about a topic not in your documents — observe what happens

**Step 4:** Consider the limitations:
- [ ] Find a case where the top result has a high score but doesn't actually answer your question
- [ ] Is this domain one where PageIndex would outperform similarity search? (See Resource 5, Section 3)

---

## How to Run It

```bash
cd week-2-knowledge/feature-5-find-the-answer/starter
pip install chromadb   # if not already installed
uvicorn main:app --reload --port 8000
```

Features 1–4 work immediately. Search returns 501 until you implement
`vector_store.py`. Open `http://localhost:8000` and click "Ask My Documents".

---

## What's Next

Feature 6 adds the **Smart Router** — combining vector retrieval with LLM
reasoning to decide when to retrieve, when to answer directly, and when to
route to an alternative architecture (KAG or PageIndex) for complex queries.
