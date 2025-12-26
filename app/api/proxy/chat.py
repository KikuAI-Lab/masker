"""OpenAI-compatible chat completions proxy with PII redaction.

POST /v1/chat/completions - Proxy endpoint that redacts PII before forwarding to LLM.
"""

import hashlib
import time
import uuid
from collections import defaultdict
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.config import settings
from app.middleware.auth import require_api_key
from app.models.proxy_schemas import ChatCompletionsRequest, RedactionMetadata
from app.services.audit import get_audit_logger
from app.services.policy import RedactionAction, get_policy_service
from app.services.redaction import redact_text

router = APIRouter(prefix="/v1", tags=["LLM Proxy"])


def _hash_value(value: str) -> str:
    """Create a short hash of a value for hash mode."""
    return hashlib.sha256(value.encode()).hexdigest()[:8]


def _apply_redaction_action(
    text: str,
    entity_type: str,
    action: RedactionAction,
) -> str:
    """Apply a specific redaction action to text.

    Args:
        text: The original text to redact.
        entity_type: The type of entity (EMAIL, PHONE, etc.)
        action: The redaction action to apply.

    Returns:
        The redacted text according to the action.
    """
    if action == RedactionAction.KEEP:
        return text
    elif action == RedactionAction.MASK:
        return "***"
    elif action == RedactionAction.PLACEHOLDER:
        return f"<{entity_type}>"
    elif action == RedactionAction.HASH:
        return f"[{_hash_value(text)}]"
    elif action == RedactionAction.DROP:
        return ""
    else:
        return "***"  # Default fallback


def _redact_message_content(
    content: str,
    policy_id: str,
    language: str = "en",
) -> tuple[str, dict[str, int]]:
    """Redact PII from message content using policy.

    Args:
        content: The message content to redact.
        policy_id: The policy ID to use.
        language: Language for NER detection.

    Returns:
        Tuple of (redacted_content, entities_by_type).
    """
    policy_service = get_policy_service()
    policy = policy_service.get(policy_id)

    # Use existing redact_text with placeholder mode to get entities
    # Then re-apply with policy-specific actions
    redacted, items = redact_text(
        text=content,
        language=language,
        entities_filter=None,
        mode="placeholder",  # We'll re-process with policy
    )

    if not items:
        return content, {}

    # Count entities by type
    entities_by_type: dict[str, int] = defaultdict(int)

    # Re-apply redaction with policy-specific actions
    # Process in reverse order to maintain positions
    result = content
    for item in sorted(items, key=lambda x: x.start, reverse=True):
        action = policy.get_action(item.entity_type)
        entities_by_type[item.entity_type] += 1

        replacement = _apply_redaction_action(
            content[item.start : item.end],
            item.entity_type,
            action,
        )
        result = result[: item.start] + replacement + result[item.end :]

    return result, dict(entities_by_type)


@router.post(
    "/chat/completions",
    summary="🔒 Chat completions with PII redaction",
    description="""
**OpenAI-compatible chat completions endpoint with automatic PII redaction.**

This endpoint:
1. Redacts PII from all message contents using the configured policy
2. Forwards the redacted request to the upstream LLM (OpenAI by default)
3. Returns the response with optional redaction metadata

## Usage

Works as a drop-in replacement for OpenAI's `/v1/chat/completions` endpoint.

```python
import openai

client = openai.OpenAI(
    base_url="https://your-masker-instance.com/v1",
    api_key="your-masker-api-key",
    default_headers={"X-Api-Key": "your-masker-api-key"}
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "My email is john@example.com"}
    ]
)
# PII is automatically redacted before reaching OpenAI
```

## Policy Selection

Use the `policy_id` field to select a specific redaction policy:
```json
{
    "model": "gpt-4",
    "messages": [...],
    "policy_id": "strict"
}
```

## Fail Modes

- **closed** (default): If redaction fails, the request is blocked.
- **open**: If redaction fails, the request is forwarded as-is (logged as error).
""",
    responses={
        401: {"description": "Missing or invalid API key"},
        502: {"description": "Upstream LLM error"},
        503: {"description": "Redaction failed in fail-closed mode"},
    },
)
async def chat_completions(
    request: Request,
    body: ChatCompletionsRequest,
    tenant_id: str = Depends(require_api_key),
) -> dict[str, Any]:
    """Handle chat completions with PII redaction.

    Args:
        request: The FastAPI request object.
        body: The chat completions request body.
        tenant_id: The authenticated tenant ID.

    Returns:
        The upstream response with optional redaction metadata.
    """
    t0 = time.perf_counter()
    request_id = str(uuid.uuid4())

    audit_logger = get_audit_logger()
    policy_service = get_policy_service()

    policy_id = body.policy_id or settings.default_policy_id
    policy = policy_service.get(policy_id)

    # Track totals
    total_entities: dict[str, int] = defaultdict(int)
    redaction_error: str | None = None

    # Redact PII in messages
    redacted_messages: list[dict[str, Any]] = []

    try:
        for msg in body.messages:
            msg_dict = msg.model_dump(exclude_none=True)

            if msg.content:
                redacted_content, entities_by_type = _redact_message_content(
                    content=msg.content,
                    policy_id=policy_id,
                )
                msg_dict["content"] = redacted_content

                for entity_type, count in entities_by_type.items():
                    total_entities[entity_type] += count

            redacted_messages.append(msg_dict)

    except Exception as e:
        redaction_error = str(e)

        if policy.fail_mode == "closed":
            # Log and reject
            redaction_ms = (time.perf_counter() - t0) * 1000
            audit_logger.log_request(
                request_id=request_id,
                endpoint="/v1/chat/completions",
                entities_by_type=dict(total_entities),
                policy_id=policy_id,
                fail_mode=policy.fail_mode,
                redaction_ms=redaction_ms,
                tenant_id=tenant_id,
                error=redaction_error,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Redaction failed (fail-closed mode): {redaction_error}",
            )
        else:
            # fail-open: use original messages
            redacted_messages = [m.model_dump(exclude_none=True) for m in body.messages]

    redaction_ms = (time.perf_counter() - t0) * 1000

    # Prepare upstream request
    upstream_body = body.model_dump(exclude_none=True, exclude={"policy_id"})
    upstream_body["messages"] = redacted_messages

    # Forward to upstream
    upstream_url = settings.upstream_url
    upstream_ms: float | None = None
    upstream_status: int | None = None

    try:
        t_upstream = time.perf_counter()

        async with httpx.AsyncClient(timeout=settings.upstream_timeout) as client:
            # Check if Authorization header is passed through
            auth_header = request.headers.get("Authorization")
            headers = {
                "Content-Type": "application/json",
            }
            if auth_header:
                headers["Authorization"] = auth_header

            response = await client.post(
                upstream_url,
                json=upstream_body,
                headers=headers,
            )

        upstream_ms = (time.perf_counter() - t_upstream) * 1000
        upstream_status = response.status_code

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Upstream error: {response.status_code} - {response.text[:200]}",
            )

        result = response.json()

    except httpx.TimeoutException:
        total_ms = (time.perf_counter() - t0) * 1000
        audit_logger.log_request(
            request_id=request_id,
            endpoint="/v1/chat/completions",
            entities_by_type=dict(total_entities),
            policy_id=policy_id,
            fail_mode=policy.fail_mode,
            redaction_ms=redaction_ms,
            tenant_id=tenant_id,
            total_ms=total_ms,
            error="Upstream timeout",
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Upstream LLM request timed out.",
        )

    except httpx.RequestError as e:
        total_ms = (time.perf_counter() - t0) * 1000
        audit_logger.log_request(
            request_id=request_id,
            endpoint="/v1/chat/completions",
            entities_by_type=dict(total_entities),
            policy_id=policy_id,
            fail_mode=policy.fail_mode,
            redaction_ms=redaction_ms,
            tenant_id=tenant_id,
            total_ms=total_ms,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream connection error: {e}",
        )

    total_ms = (time.perf_counter() - t0) * 1000

    # Log successful request
    audit_logger.log_request(
        request_id=request_id,
        endpoint="/v1/chat/completions",
        entities_by_type=dict(total_entities),
        policy_id=policy_id,
        fail_mode=policy.fail_mode,
        redaction_ms=redaction_ms,
        tenant_id=tenant_id,
        upstream_ms=upstream_ms,
        upstream_status=upstream_status,
        total_ms=total_ms,
        error=redaction_error,
    )

    # Add redaction metadata to response (optional, non-breaking)
    result["_redaction"] = RedactionMetadata(
        request_id=request_id,
        entities_total=sum(total_entities.values()),
        entities_by_type=dict(total_entities),
        policy_id=policy_id,
        redaction_ms=round(redaction_ms, 2),
        total_ms=round(total_ms, 2),
    ).model_dump()

    return result
