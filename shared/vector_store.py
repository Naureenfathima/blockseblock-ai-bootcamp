"""
Vector store for Feature 5: Find the Answer.

Wraps ChromaDB for persistent, disk-backed chunk embeddings.
Uses Chroma's built-in ONNX embedding function — no external API key
needed. Under the hood: all-MiniLM-L6-v2 producing 384-dimensional vectors.

Unlike session_store.py which resets on every restart, this vector store
persists to disk at VECTOR_DB_PATH — documents you upload survive a
server restart.

Public API:
  get_collection()                              → chromadb.Collection
  add_chunks(document_id, chunks, metadatas)    → None
  search(query, top_k, filters)                 → list[dict]
  delete_document_chunks(document_id)           → None
  get_stats()                                   → dict
"""
from pathlib import Path
from typing import Any

import chromadb

COLLECTION_NAME = "documents"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # Chroma's built-in default

_client: Any = None  # chromadb.ClientAPI — PersistentClient is a factory, not a class


def get_collection() -> chromadb.Collection:
    """
    Return the Chroma collection, creating it on first call.

    Singleton pattern: the PersistentClient is opened once per process and
    reused. The database lives at VECTOR_DB_PATH (from settings), resolved
    relative to the repo root so it's the same folder regardless of which
    feature directory the server is started from.

    Unlike session_store.py which resets on every restart, this vector store
    persists to disk — your uploaded documents survive a server restart.
    """
    global _client
    if _client is None:
        from shared.config import settings

        # Resolve path from repo root (shared/ lives one level below root)
        repo_root = Path(__file__).resolve().parent.parent
        db_path = (repo_root / settings.vector_db_path).resolve()
        db_path.mkdir(parents=True, exist_ok=True)

        _client = chromadb.PersistentClient(path=str(db_path))

    return _client.get_or_create_collection(COLLECTION_NAME)


def add_chunks(document_id: str, chunks: list[str], metadatas: list[dict]) -> None:
    """
    Embed and store document chunks with metadata.

    Chroma auto-embeds the text for us. Under the hood: each chunk becomes
    a 384-dimensional vector using the default all-MiniLM-L6-v2 model.
    We never see the numbers — we just hand Chroma the text and it handles
    the conversion.

    IDs are deterministic: "{document_id}_{i}" — so re-uploading the same
    document overwrites its vectors rather than creating duplicates.

    Args:
      document_id: the Document's UUID from document_store
      chunks:      list of raw text strings to embed and index
      metadatas:   parallel list of metadata dicts (filename, chunk_index …)
                   None values are removed — Chroma does not support null metadata.
    """
    if not chunks:
        return

    collection = get_collection()
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]

    # Inject document_id into every metadata entry so we can filter/delete by it.
    # Also strip None values — Chroma rejects them.
    cleaned_metadatas = [
        {k: v for k, v in {**m, "document_id": document_id}.items() if v is not None}
        for m in metadatas
    ]

    collection.add(documents=chunks, metadatas=cleaned_metadatas, ids=ids)


def search(
    query: str,
    top_k: int = 5,
    filters: dict | None = None,
) -> list[dict]:
    """
    Embed the query and return the top_k most similar chunks.

    Distance-to-score conversion:
      Chroma returns L2 distances. We convert to a 0.0–1.0 similarity
      score using:  score = max(0.0, 1.0 - (distance / 2.0))

      This maps:
        distance 0.0 (identical vectors)         → score 1.0
        distance 2.0 (max possible for unit vecs) → score 0.0
      Higher score = more similar. More intuitive than raw distance.

    NOTE — Similarity ≠ Relevance:
      This score measures how close two vector representations are —
      not necessarily how relevant the chunk is to answering the question.
      A chunk can be semantically similar without containing the answer.
      A chunk with the exact answer can score low if it uses different words.

      This is the core limitation of vector RAG ("vibe retrieval").
      Feature 6's Smart Router adds LLM-based reasoning on top of this
      similarity signal. PageIndex (Resource 4) replaces this step entirely
      with reasoning-based retrieval for domains where similarity falls short.

    Args:
      query:   the user's question (embedded using the same model as the chunks)
      top_k:   maximum results to return
      filters: optional Chroma `where` clause for metadata filtering.
               {"document_id": "abc"} → search within one document only.

    Returns:
      list of result dicts sorted by score (highest first):
        {"text": str, "filename": str, "chunk_index": int,
         "score": float, "document_id": str}
    """
    collection = get_collection()
    total = collection.count()
    if total == 0:
        return []

    n_results = min(top_k, total)

    kwargs: dict = {"query_texts": [query], "n_results": n_results}
    if filters:
        kwargs["where"] = filters

    results = collection.query(**kwargs)

    output = []
    for doc_text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        score = max(0.0, 1.0 - (distance / 2.0))
        output.append({
            "text": doc_text,
            "filename": meta.get("filename", ""),
            "chunk_index": meta.get("chunk_index", 0),
            "score": round(score, 4),
            "document_id": meta.get("document_id", ""),
        })

    return output


def delete_document_chunks(document_id: str) -> None:
    """
    Remove all vectors for a document from the collection.

    Called automatically by DELETE /api/documents/{id} so the vector store
    stays consistent with the document store — no orphaned vectors.
    """
    collection = get_collection()
    if collection.count() == 0:
        return
    collection.delete(where={"document_id": document_id})


def get_stats() -> dict:
    """
    Return aggregate statistics about the vector store.

    Used by GET /api/search/stats.

    Returns:
      total_vectors:     total number of chunk vectors currently indexed
      documents_indexed: number of distinct documents represented in the store
      embedding_model:   the model name used to generate the embeddings
    """
    collection = get_collection()
    total = collection.count()

    if total == 0:
        return {
            "total_vectors": 0,
            "documents_indexed": 0,
            "embedding_model": EMBEDDING_MODEL_NAME,
        }

    all_items = collection.get(include=["metadatas"])
    unique_doc_ids = {
        m.get("document_id")
        for m in all_items["metadatas"]
        if m.get("document_id")
    }

    return {
        "total_vectors": total,
        "documents_indexed": len(unique_doc_ids),
        "embedding_model": EMBEDDING_MODEL_NAME,
    }
