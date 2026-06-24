# Resource 5: Vector Database Decision Guide

**Feature 5 · AI Engineering Bootcamp · BlockseBlock**

This guide covers where vector search sits in the RAG pipeline, what an embedding
actually is, the honest limitations of similarity-based retrieval, and a comparison
of the main vector database options you'll encounter in production.

---

## Section 1: The Full RAG Pipeline

Feature 4 built the left half. Feature 5 builds the right half.

```
INGESTION (Feature 4)                   RETRIEVAL (Feature 5)
━━━━━━━━━━━━━━━━━━━━━                   ━━━━━━━━━━━━━━━━━━━━
                                        
Document                                User question
   │                                         │
   ▼                                         ▼
extract_text()                          embedding model
   │                                         │
   ▼                                         ▼
chunk_text()                            query vector
   │                                         │
   ▼                                         ▼
embedding model ──────────────────► nearest-neighbor search
   │                                         │
   ▼                                         ▼
chunk vectors stored in vector DB ───► top-k chunks returned
                                             │
                                             ▼
                                      injected into prompt
                                             │
                                             ▼
                                         LLM answer
```

The embedding model runs twice: once per chunk at ingestion, once per query
at retrieval time. Both uses must use the **same model** — otherwise the
vectors live in different spaces and similarity comparisons are meaningless.

In Feature 5 we use Chroma's built-in `all-MiniLM-L6-v2` (via ONNX) for both
steps. In production you'd typically use a dedicated embedding API (see Section 4).

---

## Section 2: What an Embedding Actually Is

An embedding model maps text → a list of numbers. The length of that list is
the **dimension** of the embedding space (all-MiniLM-L6-v2 → 384 dimensions).

**The intuition:** imagine a 2D map of meaning.

```
         [outdoors]
              ↑
  "mountain"  "hiking"  "trail"
  
                        [gear]
  "tent"   "backpack"          "laptop"
                               
              ↓               "office"
          [indoors]           "keyboard"
```

Texts with similar meaning are placed nearby on this map. The embedding model
learned these placements from enormous amounts of text during training — it
"knows" that "hiking" and "trail" are related, and that "laptop" belongs
in a different neighbourhood.

In 384 dimensions, there are 384 of these axes simultaneously. We can't
visualise them, but the geometry holds: similar meaning → close vectors.

**The nearest-neighbor search:** given a query vector, find the stored vectors
with the smallest distance. This is the only computation happening at retrieval
time. No language understanding, no reasoning — just geometric distance.

---

## Section 3: The Honest Limitation — Similarity ≠ Relevance

This is the most important thing to understand about vector RAG.

### What similarity measures

The score returned by `search()` is a measure of how close the chunk vector
and the query vector are in the embedding space. High score = the model
learned to place these texts near each other.

### What similarity does NOT measure

Whether the chunk actually answers the question. Consider:

**Query:** "What is the cancellation policy?"

Chunk A (score 0.87):
> "Our refund policy is designed with customer satisfaction in mind. We believe
>  in transparent and fair policy enforcement across all transaction types."

Chunk B (score 0.61):
> "Cancellations received more than 14 days before the event date receive a
>  full refund. Cancellations within 14 days are non-refundable."

Chunk A has high similarity because it shares vocabulary (policy, refund) but
doesn't answer the question. Chunk B answers the question precisely but scored
lower because it uses more specific and less "similar" language.

This is "vibe retrieval" — the model retrieves passages that *sound like* the
question rather than passages that *answer* the question.

### When it matters most

The similarity≠relevance gap is widest in:

- **Professional documents** — financial reports, legal filings, technical manuals.
  These documents use precise vocabulary that differs significantly from how
  users phrase questions. ("net revenue attributable to continued operations"
  vs "how much did the company make?")

- **Multi-hop queries** — questions where the answer requires connecting
  information from multiple sections. Similarity search retrieves individual
  passages, not chains of reasoning.

- **Defined-term documents** — legal contracts and regulatory filings use
  terms that are defined in one section and used in another. Similarity search
  can't follow these cross-references.

### When it works fine

For general knowledge bases — product FAQs, internal wikis, support docs —
similarity search works well. The vocabulary users and documents use overlaps
enough that "close in vector space" approximates "relevant to the question."

### The fix

**Feature 6:** Smart Router adds LLM-based relevance scoring on top of
similarity — asks the LLM "is this chunk actually relevant to this question?"
and filters or reranks results. Works for general domains.

**PageIndex:** Replaces the similarity step entirely with tree navigation by
reasoning. Works best for professional long documents. See Section 5.

---

## Section 4: Vector Database Comparison

All of these can store and search chunk embeddings. The differences are in
where the data lives, what scales, and what you have to operate.

| | Chroma | Pinecone | pgvector | Weaviate | Qdrant | FAISS | Cloud options |
|---|---|---|---|---|---|---|---|
| **Type** | Library | Managed | Postgres extension | Managed/self-hosted | Managed/self-hosted | Library | AWS/Azure/GCP native |
| **Free tier** | ✅ Fully local | ✅ Starter tier | ✅ (with Postgres) | ✅ Limited cloud | ✅ Free cloud | ✅ Open source | Varies |
| **Setup complexity** | Low | Low | Medium | Medium | Low | Low | Medium-High |
| **Persistence** | Disk (PersistentClient) | Managed | Postgres | Managed | Managed | Manual | Managed |
| **Scale** | Millions of vectors | Billions | Depends on Postgres | Millions+ | Millions+ | Millions (RAM) | Managed |
| **Auto-embed** | Yes (built-in model) | No | No | Yes | No | No | Varies |
| **Metadata filtering** | Yes | Yes | Yes (SQL) | Yes | Yes | Limited | Varies |
| **Best for** | Development, prototyping | Production serverless | Teams already on Postgres | Multi-modal, large scale | High-performance search | Offline, no server | Existing cloud infra |

**Why we use Chroma in this course:**
- Runs entirely on your laptop — no account, no API key, no network dependency
- Auto-embeds using a bundled ONNX model (all-MiniLM-L6-v2)
- PersistentClient stores data to disk so your vectors survive server restarts
- `pip install chromadb` and you're done

**When to move to Pinecone/Qdrant/Weaviate:**
- Document volume exceeds ~1M chunks and local disk becomes a bottleneck
- You need managed backups, SLAs, or multi-region replication
- Your team already has a Postgres stack → pgvector is the natural choice

**Cloud-native options:**
- **AWS:** Amazon OpenSearch with k-NN plugin, or store in S3 and use Bedrock Knowledge Bases
- **Azure:** Azure AI Search (formerly Cognitive Search) with vector fields
- **GCP:** Vertex AI Matching Engine (now called Vector Search)

These are all the same concept (nearest-neighbor search over dense vectors)
wrapped in different managed services.

---

## Section 5: PageIndex as the Alternative to Vector Retrieval

When similarity-based retrieval consistently produces wrong answers despite
tuning chunk size and overlap, the problem may not be the vector database —
it may be the fundamental approach of similarity-based retrieval.

**PageIndex** (github.com/VectifyAI/PageIndex, MIT licence) takes a completely
different approach:

1. **Builds a hierarchical tree index** from the document — like a smart table
   of contents. Each tree node has a title, page range, and LLM-generated
   summary of what that section contains.

2. **Retrieves by LLM reasoning** — an LLM agent navigates the tree the way
   a human expert flips through a complex report, asking "is the answer in
   this section?" at each node. No vectors. No similarity. No embeddings.

**Result on FinanceBench:** 98.7% accuracy vs significantly lower for
traditional vector RAG systems on financial document Q&A.

### Which document types benefit most from PageIndex

| Document type | Problem with vector RAG | PageIndex advantage |
|---|---|---|
| Annual reports / 10-Ks | Revenue figures appear in many sections with similar phrasing | Navigates directly to segment reporting |
| Legal contracts | Defined terms used far from their definitions | Traverses structure to find definition + usage |
| Technical manuals | Part numbers and specifications embedded in structured tables | Tree navigation reaches the right section |
| Regulatory filings | Cross-references between sections | Follows section hierarchy |
| Financial statements | Same number appears in multiple contexts | Navigates to the precise context |

### Integration path (Feature 6)

Feature 6's Smart Router adds a routing decision:
- General knowledge queries → vector RAG (Feature 5)
- Professional document queries → PageIndex tree search

```bash
pip install -r requirements.txt  # from github.com/VectifyAI/PageIndex
python run_pageindex.py --pdf_path your_report.pdf  # builds tree JSON
# Feature 6: route based on document type and query complexity
```

---

## Section 6: LangChain VectorStore Equivalents

If you use LangChain in production, here's how `shared/vector_store.py`
maps to its abstractions:

| `shared/vector_store.py` | LangChain |
|---|---|
| `get_collection()` | `Chroma(persist_directory=..., embedding_function=...)` |
| `add_chunks(texts, metas)` | `vectorstore.add_texts(texts, metadatas=metas)` |
| `search(query, top_k)` | `vectorstore.similarity_search_with_score(query, k=top_k)` |
| `delete_document_chunks(doc_id)` | `vectorstore.delete(ids=[...])` |
| Distance-to-score: `1.0 - (d / 2.0)` | Done internally by LangChain before returning scores |
| `filters` dict | `vectorstore.similarity_search(query, filter={...})` |

**The difference:** LangChain wraps all of this in a unified interface so you
can swap Chroma for Pinecone with one line change. Building it yourself first
means you understand exactly what the abstraction is doing — and can debug it
when the abstraction leaks.

---

## Worksheet

1. Upload a document and run these three searches. Record the top result's score each time:
   - A question using the same words as the document
   - A question meaning the same thing but using different words
   - A question about a topic not in the document
   
   What do the scores tell you? What don't they tell you?

2. Find one result where the score is high but the chunk doesn't actually answer your question.
   Why did that chunk score high? What vocabulary caused it?

3. Is your domain one where PageIndex would outperform vector RAG?
   Use Section 3's checklist: professional documents, multi-hop queries, defined terms?

4. If you were building a knowledge base for a law firm's contract management system,
   which vector DB from Section 4 would you choose, and why?
   At what document volume would you change your answer?
