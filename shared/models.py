"""
Shared Pydantic models for the AI Engineering Bootcamp.

This file holds data models that are used by more than one feature.
Each feature may also define its own local models inside its own directory.

New models are added here as they are introduced in the course:
  - Feature 2 adds: StructuredResponse
  - Feature 3 adds: Message, Session
  - Feature 4 adds: Document, Chunk
  - Feature 8 adds: ToolDefinition, ToolCall
"""
from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field


# =============================================================================
# Feature 2: Structured output
# =============================================================================

class StructuredResponse(BaseModel):
    """
    A structured reply from the AI assistant that includes classification metadata
    alongside the answer text.

    Instead of returning plain text, the assistant analyzes the query, decides
    what kind of question it is, and returns that classification together with its
    answer and a confidence estimate. This lets the UI (and any downstream code)
    make decisions based on the *type* of question — for example, showing a
    warning when confidence is low, or routing action requests to a separate flow.
    """

    intent: Literal["general_question", "domain_question", "action_request", "unclear"] = Field(
        description=(
            "What kind of request the user made. "
            "'general_question' = factual/knowledge query unrelated to the domain. "
            "'domain_question' = a question specifically about the assistant's domain. "
            "'action_request' = the user wants something DONE (book, schedule, find, send, etc.). "
            "'unclear' = the query is ambiguous or doesn't fit the other categories."
        )
    )

    answer: str = Field(
        description=(
            "The assistant's response to the user's query, written in plain English. "
            "For action_request intents, this should explain what action would be taken "
            "and any information still needed to complete it."
        )
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How confident the assistant is in its answer, from 0.0 (not confident at all) "
            "to 1.0 (completely certain). A confidence below 0.5 usually means the answer "
            "should be verified — this is surfaced visually in the UI."
        ),
    )

    sources_needed: bool = Field(
        description=(
            "True if this answer would be significantly better with access to domain documents "
            "(uploaded in Feature 4+). False if the answer is reliably answerable from "
            "general knowledge or the system prompt alone. "
            "This flag is used in Week 2 to decide whether to trigger RAG retrieval."
        )
    )


# =============================================================================
# Feature 3: Conversation memory
# =============================================================================

class Message(BaseModel):
    """
    A single message in a conversation — either from the user or the assistant.

    Messages are stored in order inside a Session and sent to the LLM as
    conversation history so the assistant can refer back to earlier exchanges.
    """

    role: Literal["user", "assistant"] = Field(
        description=(
            "Who sent this message. 'user' is the person typing; "
            "'assistant' is the AI's reply."
        )
    )

    content: str = Field(
        description="The text of the message."
    )

    timestamp: datetime = Field(
        description="When this message was recorded, in UTC."
    )


class Session(BaseModel):
    """
    A single conversation thread between a user and the assistant.

    A session holds the full ordered history of messages for one conversation.
    When the user starts a 'New Chat', a new session is created with a fresh
    empty history — previous sessions remain accessible in the sidebar.
    """

    id: str = Field(
        description="Unique identifier for this session (a UUID)."
    )

    created_at: datetime = Field(
        description="When this session was started, in UTC."
    )

    messages: List[Message] = Field(
        default_factory=list,
        description=(
            "All messages in this conversation, oldest first. "
            "The assistant uses this list as context when generating each new reply."
        ),
    )


# =============================================================================
# Feature 4: Document ingestion
# =============================================================================

class Document(BaseModel):
    """
    Metadata record for an uploaded document.

    When a file is uploaded it immediately gets a Document record with
    status='processing'. Once text extraction and chunking complete, status
    flips to 'ready' and chunk_count is updated. On failure: 'error'.

    The extracted text itself is NOT stored here — chunks are stored separately
    in Chunk objects. This keeps the metadata record lightweight.
    """

    id: str = Field(
        description="Unique identifier for this document (a UUID)."
    )

    filename: str = Field(
        description="Original filename as uploaded by the user (e.g. 'report.pdf')."
    )

    uploaded_at: datetime = Field(
        description="When this document was uploaded, in UTC."
    )

    status: Literal["processing", "ready", "error"] = Field(
        description=(
            "'processing' while text is being extracted and chunked. "
            "'ready' once chunks are stored and available for retrieval. "
            "'error' if extraction or chunking failed."
        )
    )

    chunk_count: int = Field(
        default=0,
        description="Number of text chunks created from this document. 0 while processing.",
    )

    chunking_strategy: str = Field(
        default="sentence",
        description=(
            "Which chunking strategy was used during ingestion. "
            "One of: 'sentence' (sentence-aware fixed-size, default), "
            "'paragraph' (paragraph-based), 'page' (one chunk per PDF page). "
            "Stored so the UI can display it and future re-ingestion can reproduce the same split."
        ),
    )


class Chunk(BaseModel):
    """
    A single text chunk extracted from a Document.

    Documents are split into chunks so that only the most relevant passages
    are sent to the LLM on each query (RAG). Each Chunk stores the text and
    its position within the source document.

    In Feature 5 these chunks are converted to vector embeddings for semantic search.
    """

    id: str = Field(
        description="Unique identifier for this chunk (a UUID)."
    )

    document_id: str = Field(
        description="ID of the Document this chunk belongs to."
    )

    text: str = Field(
        description="The raw text content of this chunk."
    )

    chunk_index: int = Field(
        description="Zero-based position of this chunk within its document. Chunk 0 is the first."
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Arbitrary key-value metadata. At minimum contains 'filename' and 'chunk_index'. "
            "Feature 5 may add 'embedding_model', 'token_count', etc."
        ),
    )
