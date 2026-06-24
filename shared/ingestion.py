"""
Text extraction and chunking for Feature 4: Feed the Brain.

ARCHITECTURE CHOICE — FOUR WAYS TO GIVE AN LLM EXTERNAL KNOWLEDGE
(see README for the full comparison and decision guide):

  RAG (Retrieval-Augmented Generation) — what this module implements.
    Documents → chunk → embed → vector DB. At query time, find the relevant
    chunks by semantic similarity and inject them. Scales to many documents.
    Core limitation: "vibe retrieval" — similarity ≠ relevance.

  CAG (Cache-Augmented Generation) — skips this module entirely.
    Load ALL document text directly into the system prompt; the model's KV
    cache is pre-computed once and reused. No retrieval step, no chunking
    errors. Only viable for small, stable doc sets (<~50 pages total).

  KAG (Knowledge-Augmented Generation) — uses this module's extract_text(),
    then builds a knowledge graph (entities + relationships) instead of a
    vector DB. Best for relational/factual queries. Introduced in Feature 6.

  PageIndex (Vectorless, Reasoning-based) — builds a hierarchical tree index
    (like a TOC optimised for LLMs); an LLM agent navigates the tree to find
    the relevant section using reasoning, not similarity. No chunking, no
    embeddings, no vector DB. By VectifyAI (github.com/VectifyAI/PageIndex,
    MIT licence). 98.7% on FinanceBench vs significantly lower for vector RAG.
    Best for long professional docs (financial reports, legal filings).
    See PAGEINDEX_NOTE below.

CHOOSE YOUR PATH:
  - CAG:       < ~50 pages total, stable docs, zero retrieval errors required
               → skip this module, load raw text into system prompt directly
  - KAG:       relational/factual queries ("how does X relate to Y?")
               → extract_text() + build knowledge graph (see Feature 6)
  - PageIndex: long professional docs (financial/legal), reasoning required
               → no chunking at all, build hierarchical tree (VectifyAI)
  - RAG:       multiple/large docs, semantic questions, need to scale
               → this is what we build here (chunk → embed → retrieve)

Public API:
  extract_text(file_bytes, filename)  → str
  extract_pages(file_bytes, filename) → list[dict]  (page_number + text per page)
  chunk_text(text, ...)               → list[str]   (sentence-aware fixed-size)
  chunk_by_paragraph(text, ...)       → list[str]   (paragraph-based)
  chunk_by_page(pages, ...)           → list[dict]  (one entry per page, with page_number)
  CHUNKING_STRATEGIES                 → dict mapping strategy name → callable
"""
import io
import re
from pathlib import Path
from typing import Callable


# =============================================================================
# Extraction
# =============================================================================

def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract plain text from uploaded file bytes.

    Dispatches based on file extension:
      .txt  — decode as UTF-8 (no extra library needed)
      .pdf  — extract page-by-page with pypdf, join pages with newlines
      .docx — extract paragraphs with python-docx

    For PDFs, page text is joined with newlines. If you need per-page
    structure, call extract_pages() instead.

    Raises:
      ValueError: if the file extension is not supported.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".txt":
        return file_bytes.decode("utf-8", errors="replace")

    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if ext == ".docx":
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

    raise ValueError(
        f"Unsupported file type: '{ext}'. "
        "Supported formats: .txt, .pdf, .docx. "
        "Convert your file to one of these formats and re-upload."
    )


def extract_pages(file_bytes: bytes, filename: str) -> list[dict]:
    """
    Extract text per page, returning a list of dicts with page_number and text.

    For .pdf: one dict per page (page_number is 1-based).
    For .txt and .docx: single dict with page_number=1 and full text.

    Used by chunk_by_page() to preserve page-level metadata in chunks.

    Returns:
      list of {"page_number": int, "text": str} — always at least one entry.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        return [
            {"page_number": i + 1, "text": page.extract_text() or ""}
            for i, page in enumerate(reader.pages)
        ]

    # Non-PDF: treat the whole file as page 1.
    return [{"page_number": 1, "text": extract_text(file_bytes, filename)}]


# =============================================================================
# Chunking strategies
# =============================================================================

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Strategy: Sentence-aware fixed-size chunking (Strategy 2 in Resource 4).

    Split on sentence boundaries (. ! ?), group sentences until ~chunk_size
    characters, carry ~overlap characters from the previous chunk's tail into
    the next for context continuity. Never cuts mid-sentence.

    This is the default strategy — works well for most document types.

    Args:
      text:       full document text
      chunk_size: target character length per chunk (default 500)
      overlap:    characters from previous chunk tail to carry forward (default 50)

    Returns:
      list of non-empty chunk strings
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        slen = len(sentence)

        if current and current_len + slen > chunk_size:
            chunks.append(" ".join(current))

            # Overlap tail: carry back sentences until we reach ~overlap chars.
            tail: list[str] = []
            tail_len = 0
            for s in reversed(current):
                if tail_len + len(s) + 1 > overlap:
                    break
                tail.insert(0, s)
                tail_len += len(s) + 1

            current = tail
            current_len = tail_len

        current.append(sentence)
        current_len += slen + 1

    if current:
        chunks.append(" ".join(current))

    return chunks


def chunk_by_paragraph(text: str, max_chunk_size: int = 800) -> list[str]:
    """
    Strategy: Paragraph-based chunking (Strategy 3 in Resource 4).

    Split on double newlines (paragraph breaks). If a single paragraph
    exceeds max_chunk_size, fall back to sentence-aware splitting for
    that paragraph only — so the output always fits the size budget.

    Best for: formal structured documents — policies, manuals, legal text —
    where each paragraph is already a coherent unit of thought.

    Args:
      text:           full document text
      max_chunk_size: maximum character length per chunk (default 800)

    Returns:
      list of non-empty chunk strings
    """
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    chunks: list[str] = []

    for para in paragraphs:
        if len(para) <= max_chunk_size:
            chunks.append(para)
        else:
            # Paragraph is too long — fall back to sentence-aware splitting.
            chunks.extend(chunk_text(para, chunk_size=max_chunk_size))

    return chunks


def chunk_by_page(pages: list[dict], max_page_size: int = 2000) -> list[dict]:
    """
    Strategy: pageIndex — one chunk per page of the original document.

    Each returned dict has:
      "text":        the page text (or sub-chunk if the page was very long)
      "page_number": the 1-based page number from the source PDF
      "chunk_index": zero-based position across all chunks in this document

    If a single page exceeds max_page_size, it is further split using
    chunk_text() — all resulting sub-chunks keep the same page_number.

    When to use:
      Financial reports, legal filings, academic papers, or any document where
      'see page X' is a meaningful citation unit. The page_number in each
      chunk's metadata lets the assistant cite the exact page to the user.

    Advantage over sentence chunking: preserves document structure.
    Disadvantage: page sizes vary wildly — a dense page may produce a very
    large chunk; a section header page may produce a near-empty one.

    Args:
      pages:         list of {"page_number": int, "text": str} from extract_pages()
      max_page_size: character limit before a page is sub-chunked (default 2000)

    Returns:
      list of {"text": str, "page_number": int, "chunk_index": int}
    """
    result: list[dict] = []
    chunk_index = 0

    for page in pages:
        text = page["text"].strip()
        page_num = page["page_number"]

        if not text:
            continue

        if len(text) <= max_page_size:
            result.append({
                "text": text,
                "page_number": page_num,
                "chunk_index": chunk_index,
            })
            chunk_index += 1
        else:
            for sub in chunk_text(text, chunk_size=max_page_size):
                result.append({
                    "text": sub,
                    "page_number": page_num,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1

    return result


# =============================================================================
# CAG ALTERNATIVE (Cache-Augmented Generation)
# Not implemented here — shown as a documented pattern for comparison.
#
# Instead of chunking, concatenate ALL document text and pass it directly
# in the system prompt. The model's KV cache is computed once on the full
# context and reused across queries — no retrieval step, no vector DB,
# no chunking errors.
#
# When to use:
#   • Total document set is small (< ~50 pages / ~100K tokens)
#   • Documents change infrequently (cache must be recomputed on each change)
#   • Retrieval precision is critical (you can't afford a missed chunk)
#   • You're using a large-context model (Gemini 1.5 Pro: 1M tokens, GPT-4o: 128K)
#
# Pattern (not wired up — for reference only):
#
#   all_text = "\n\n---\n\n".join(
#       extract_text(file_bytes, filename) for file_bytes, filename in documents
#   )
#   system_prompt = (
#       "Here is all relevant knowledge:\n\n"
#       f"{all_text}\n\n"
#       "Answer the user's question using only the knowledge above."
#   )
#   result = await call_llm([
#       {"role": "system", "content": system_prompt},
#       {"role": "user",   "content": user_query},
#   ])
#
# Compare with RAG: RAG retrieves the 2-3 most relevant chunks; CAG sends
# everything. CAG eliminates retrieval errors but costs more tokens per query
# and breaks once document volume grows beyond the context window.
# =============================================================================


# =============================================================================
# PAGEINDEX NOTE (Vectorless, Reasoning-based RAG) — documented pattern, not implemented here.
#
# VectifyAI's PageIndex (github.com/VectifyAI/PageIndex, MIT licence) takes a
# fundamentally different approach to document Q&A:
#
#   1. Build a HIERARCHICAL TREE INDEX from the document — like a table of
#      contents but optimised for LLMs. Each tree node has a title, a page
#      range, and an LLM-generated summary of what that section contains.
#
#   2. Retrieve by REASONING over the tree — an LLM agent navigates the tree
#      to find the most relevant section, simulating how a human expert
#      flips through a complex report. No vector similarity is used at all.
#
# Key insight from the PageIndex paper: "similarity ≠ relevance."
#   Vector RAG returns semantically similar passages.
#   PageIndex returns the passages an expert would find.
#   On FinanceBench: PageIndex 98.7% vs significantly lower for vector RAG.
#
# When to use PageIndex instead of this module:
#   • Long professional documents: financial reports, legal filings, technical
#     manuals, regulatory documents with complex structures.
#   • Multi-step reasoning needed: "What is the net revenue impact of the
#     restructuring charges disclosed on the segment reporting page?"
#   • Chunking + vector search consistently produces wrong answers.
#
# Integration path for Feature 6 (Smart Router):
#   pip install -r requirements.txt  # from github.com/VectifyAI/PageIndex
#   python run_pageindex.py --pdf_path your_doc.pdf  # generates tree JSON
#   Route queries about professional docs → PageIndex tree search
#   Route general knowledge queries     → vector RAG (Features 4-6)
#   Route relational queries            → knowledge graph (KAG, Feature 6)
#
# Cloud service + MCP server also available at pageindex.ai.
# =============================================================================


# =============================================================================
# Strategy registry — wires strategy name strings to callable chunking functions.
# Only "sentence" and "paragraph" are selectable via the upload endpoint.
# chunk_by_page() is available as a reference implementation above.
# =============================================================================

def _sentence_strategy(text: str, pages: list[dict]) -> list[dict]:
    return [
        {"text": c, "page_number": None, "chunk_index": i}
        for i, c in enumerate(chunk_text(text))
    ]


def _paragraph_strategy(text: str, pages: list[dict]) -> list[dict]:
    return [
        {"text": c, "page_number": None, "chunk_index": i}
        for i, c in enumerate(chunk_by_paragraph(text))
    ]


CHUNKING_STRATEGIES: dict[str, Callable[[str, list[dict]], list[dict]]] = {
    "sentence":  _sentence_strategy,
    "paragraph": _paragraph_strategy,
    # "page": chunk_by_page is available above as a reference implementation
    # but not wired here — see PAGEINDEX_NOTE for a more powerful page-based approach.
}
