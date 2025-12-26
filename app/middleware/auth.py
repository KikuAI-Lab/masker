"""Authentication middleware and dependencies.

Provides FastAPI dependencies for API key authentication.
"""


from fastapi import Header, HTTPException, Request, status

from app.services.api_keys import get_api_key_service


async def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
) -> str:
    """Dependency that requires a valid API key.

    Extracts tenant_id and stores it in request.state.

    Args:
        request: The FastAPI request object.
        x_api_key: API key from X-Api-Key header.

    Returns:
        The tenant ID associated with the API key.

    Raises:
        HTTPException: If API key is missing or invalid.
    """
    service = get_api_key_service()

    # If no keys configured, allow all requests (dev mode)
    if not service.is_enabled():
        request.state.tenant_id = "anonymous"
        return "anonymous"

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-Api-Key header.",
        )

    tenant_id = service.validate(x_api_key)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    # Store tenant_id in request state for logging/audit
    request.state.tenant_id = tenant_id
    return tenant_id


async def optional_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
) -> str | None:
    """Dependency that optionally validates an API key.

    Does not require a key, but validates if present.

    Args:
        request: The FastAPI request object.
        x_api_key: Optional API key from X-Api-Key header.

    Returns:
        The tenant ID if valid key provided, None otherwise.
    """
    service = get_api_key_service()

    if not x_api_key:
        request.state.tenant_id = None
        return None

    tenant_id = service.validate(x_api_key)
    request.state.tenant_id = tenant_id
    return tenant_id
