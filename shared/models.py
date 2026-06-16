"""
Shared Pydantic models for the AI Engineering Bootcamp.

This file holds data models that are used by more than one feature.
Each feature may also define its own local models inside its own directory.

New models are added here as they are introduced in the course:
  - Feature 2 adds: StructuredResponse
  - Feature 3 adds: Message, Session
  - Feature 4 adds: Document, UploadedFile
  - Feature 8 adds: ToolDefinition, ToolCall
"""
from datetime import datetime
from typing import List, Literal

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
