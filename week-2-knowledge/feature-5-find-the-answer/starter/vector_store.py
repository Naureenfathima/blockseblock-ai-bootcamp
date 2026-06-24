"""
Feature 5 starter: vector store — YOUR IMPLEMENTATION GOES HERE.

The complete version lives in shared/vector_store.py (read it for reference).

WHAT THIS MODULE DOES:
  Every time a document is uploaded, its text chunks are converted to numeric
  vectors (embeddings) and stored in a local ChromaDB database on disk. When
  a user asks a question, their question is also converted to a vector, and
  we find the stored chunks whose vectors are nearest to the question vector.

  Text → numbers → geometric space → nearest-neighbor search.
  That is all semantic search is.

CHROMA'S DEFAULT EMBEDDING FUNCTION:
  We don't write any embedding code ourselves. When we call collection.add()
  with plain text, Chroma automatically converts it to vectors using an
  ONNX-optimised version of all-MiniLM-L6-v2 (384 dimensions). We never see
  the numbers — we just hand over the text and get back similarity results.

YOUR TASKS:
  Step 1: implement the collection.add() call in add_chunks() (Step 1)
  Step 2: implement the collection.query() call in search()   (Step 2)
          + the distance-to-score conversion                  (Step 3)

Provided complete (read, don't rewrite):
  get_collection()           — database connection singleton
  delete_document_chunks()   — cleanup on document delete
  get_stats()                — aggregate statistics
"""
from pathlib import Path
from typing import Any

import chromadb

COLLECTION_NAME = "documents"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

_client: Any = None  # chromadb.ClientAPI — PersistentClient is a factory, not a class


# =============================================================================
# Provided complete — do NOT modify
# =============================================================================

def get_collection() -> chromadb.Collection:
    """
    Return the Chroma collection, creating it on first call.

    Singleton pattern: opens the database once per process and reuses it.
    Persists to disk at VECTOR_DB_PATH — unlike session_store.py which
    resets on every restart, this database survives server restarts.
    """
    global _client
    if _client is None:
        from shared.config import settings
        repo_root = Path(__file__).resolve().parents[3]
        db_path = (repo_root / settings.vector_db_path).resolve()
        db_path.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(db_path))
    return _client.get_or_create_collection(COLLECTION_NAME)


def delete_document_chunks(document_id: str) -> None:
    """Remove all vectors for a document from the collection."""
    collection = get_collection()
    if collection.count() == 0:
        return
    collection.delete(where={"document_id": document_id})


def get_stats() -> dict:
    """Return aggregate statistics about the vector store."""
    collection = get_collection()
    total = collection.count()
    if total == 0:
        return {"total_vectors": 0, "documents_indexed": 0, "embedding_model": EMBEDDING_MODEL_NAME}
    all_items = collection.get(include=["metadatas"])
    unique_doc_ids = {m.get("document_id") for m in all_items["metadatas"] if m.get("document_id")}
    return {"total_vectors": total, "documents_indexed": len(unique_doc_ids), "embedding_model": EMBEDDING_MODEL_NAME}


# =============================================================================
# YOUR IMPLEMENTATION
# =============================================================================

def add_chunks(document_id: str, chunks: list[str], metadatas: list[dict]) -> None:
    """
    Embed and store document chunks with metadata.

    Chroma auto-embeds for us — we just pass the raw text. Under the hood,
    each chunk becomes a 384-dimensional vector (all-MiniLM-L6-v2). We never
    see the numbers; we just hand over text and let Chroma handle conversion.

    IDs are deterministic: "{document_id}_{i}" so re-uploading overwrites
    existing vectors rather than creating duplicates.

    Args:
      document_id: the Document's UUID (from document_store)
      chunks:      list of text strings to embed and store
      metadatas:   parallel metadata dicts (filename, chunk_index, strategy)
    """
    if not chunks:
        return

    collection = get_collection()
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]

    # Add document_id to metadata and remove None values (Chroma rejects them).
    cleaned_metadatas = [
        {k: v for k, v in {**m, "document_id": document_id}.items() if v is not None}
        for m in metadatas
    ]

    # TODO (Feature 5, Step 1): call collection.add() to embed and store the chunks.
    #
    # collection.add(
    #     documents=chunks,           # list[str] — Chroma embeds these automatically
    #     metadatas=cleaned_metadatas, # list[dict] — stored alongside each vector
    #     ids=ids,                    # list[str]  — unique ID per chunk
    # )
    raise NotImplementedError(
        "Implement the collection.add() call — see the TODO above (Step 1)."
    )


def search(
    query: str,
    top_k: int = 5,
    filters: dict | None = None,
) -> list[dict]:
    """
    Embed the query and return the top_k most similar chunks.

    Distance-to-score conversion:
      Chroma returns L2 distances. We flip to a 0.0–1.0 similarity score:
        score = max(0.0, 1.0 - (distance / 2.0))
      distance 0 (identical) → score 1.0
      distance 2 (opposite)  → score 0.0
      Higher = more similar. More intuitive than raw distance.

    NOTE — Similarity ≠ Relevance:
      This score measures vector closeness, not answer quality. A chunk can
      be semantically similar to your question without containing the answer.
      This is the core limitation of vector RAG ("vibe retrieval").
      Feature 6 adds LLM reasoning on top. PageIndex replaces this step
      entirely for domains where similarity consistently falls short.

    Args:
      query:   the user's question (embedded using the same model)
      top_k:   maximum results to return
      filters: optional Chroma `where` clause, e.g. {"document_id": "abc"}

    Returns:
      list of dicts: {"text", "filename", "chunk_index", "score", "document_id"}
    """
    collection = get_collection()
    total = collection.count()
    if total == 0:
        return []

    n_results = min(top_k, total)

    kwargs: dict = {"query_texts": [query], "n_results": n_results}
    if filters:
        kwargs["where"] = filters

    # TODO (Feature 5, Step 2): call collection.query() to find similar chunks.
    #
    # results = collection.query(**kwargs)
    #
    # The results dict has these keys (each a list-of-lists, one per query):
    #   results["documents"][0]  → list[str]   — the chunk texts
    #   results["metadatas"][0]  → list[dict]  — metadata for each chunk
    #   results["distances"][0]  → list[float] — L2 distances (lower = more similar)
    raise NotImplementedError(
        "Implement collection.query() — see the TODO above (Step 2)."
    )

    # TODO (Feature 5, Step 3): convert distances to scores and build output.
    #
    # output = []
    # for doc_text, meta, distance in zip(
    #     results["documents"][0],
    #     results["metadatas"][0],
    #     results["distances"][0],
    # ):
    #     score = max(0.0, 1.0 - (distance / 2.0))  # flip: lower distance = higher score
    #     output.append({
    #         "text": doc_text,
    #         "filename": meta.get("filename", ""),
    #         "chunk_index": meta.get("chunk_index", 0),
    #         "score": round(score, 4),
    #         "document_id": meta.get("document_id", ""),
    #     })
    # return output
