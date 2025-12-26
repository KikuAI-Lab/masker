"""Pydantic schemas for OpenAI-compatible proxy endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: Literal["system", "user", "assistant", "function", "tool"] = Field(
        ...,
        description="The role of the message author."
    )
    content: str | None = Field(
        default=None,
        description="The content of the message."
    )
    name: str | None = Field(
        default=None,
        description="Optional name for the message author."
    )

    model_config = {
        "extra": "allow"  # Allow additional fields like tool_calls
    }


class ChatCompletionsRequest(BaseModel):
    """Request schema for OpenAI-compatible /v1/chat/completions endpoint."""

    model: str = Field(
        ...,
        description="Model identifier (e.g., gpt-4, gpt-3.5-turbo)."
    )
    messages: list[ChatMessage] = Field(
        ...,
        min_length=1,
        description="The messages to generate completions for."
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0-2)."
    )
    top_p: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling probability."
    )
    max_tokens: int | None = Field(
        default=None,
        gt=0,
        description="Maximum tokens to generate."
    )
    stream: bool | None = Field(
        default=False,
        description="Whether to stream partial responses."
    )

    # Masker-specific fields
    policy_id: str | None = Field(
        default=None,
        description="Masker policy ID for redaction. If not specified, uses default policy."
    )

    model_config = {
        "extra": "allow"  # Allow additional OpenAI fields
    }


class RedactionMetadata(BaseModel):
    """Metadata about redaction performed on the request."""

    request_id: str = Field(
        ...,
        description="Unique request identifier for audit."
    )
    entities_total: int = Field(
        default=0,
        description="Total number of PII entities detected and redacted."
    )
    entities_by_type: dict[str, int] = Field(
        default_factory=dict,
        description="Count of entities by type."
    )
    policy_id: str = Field(
        default="default",
        description="Policy ID used for redaction."
    )
    redaction_ms: float = Field(
        ...,
        description="Time spent on redaction in milliseconds."
    )
    total_ms: float = Field(
        ...,
        description="Total request processing time in milliseconds."
    )
