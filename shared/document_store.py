"""
In-memory document store for Feature 4: Feed the Brain.

Parallel to session_store.py (Feature 3) — same dict-backed pattern,
same create / read / write / list / delete interface.

FRAMEWORK EQUIVALENTS:
  _documents dict  ≈  a database table (documents)
  _chunks dict     ≈  a database table (chunks) with FK to documents
  delete_document  ≈  CASCADE DELETE in SQL

In Feature 11 (Docker/deploy) this can be swapped for a real database
with no changes to any endpoint — only this file changes.
"""
import uuid
from datetime import datetime, timezone

from shared.models import Chunk, Document

_documents: dict[str, Document] = {}
_chunks: dict[str, list[Chunk]] = {}  # keyed by document_id


def save_document(filename: str) -> Document:
    """
    Create a new Document record (status='processing') and store it.

    Returns the Document immediately so the endpoint can respond while
    extraction and chunking proceed (synchronously in this feature).
    chunking_strategy is updated by update_document() once ingestion completes.
    """
    doc = Document(
        id=str(uuid.uuid4()),
        filename=filename,
        uploaded_at=datetime.now(tz=timezone.utc),
        status="processing",
        chunk_count=0,
        chunking_strategy="sentence",  # placeholder; updated by update_document
    )
    _documents[doc.id] = doc
    return doc


def update_document(
    doc_id: str,
    *,
    status: str,
    chunk_count: int,
    chunking_strategy: str = "sentence",
) -> None:
    """Update a document's status, chunk_count, and chunking_strategy after processing."""
    doc = _documents.get(doc_id)
    if doc is None:
        return
    _documents[doc_id] = doc.model_copy(update={
        "status": status,
        "chunk_count": chunk_count,
        "chunking_strategy": chunking_strategy,
    })


def get_document(doc_id: str) -> Document | None:
    """Return the Document for the given ID, or None if not found."""
    return _documents.get(doc_id)


def list_documents() -> list[Document]:
    """Return all documents, most recently uploaded first."""
    return sorted(_documents.values(), key=lambda d: d.uploaded_at, reverse=True)


def save_chunk(chunk: Chunk) -> None:
    """Append a Chunk to its document's chunk list."""
    if chunk.document_id not in _chunks:
        _chunks[chunk.document_id] = []
    _chunks[chunk.document_id].append(chunk)


def get_chunks(document_id: str) -> list[Chunk]:
    """Return all chunks for a document, in order."""
    return sorted(_chunks.get(document_id, []), key=lambda c: c.chunk_index)


def delete_document(doc_id: str) -> bool:
    """
    Delete a document and all its chunks.

    Returns True if the document existed and was deleted, False if not found.
    """
    if doc_id not in _documents:
        return False
    del _documents[doc_id]
    _chunks.pop(doc_id, None)
    return True
