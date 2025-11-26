"""Masker API - PII Redaction & Text Anonymization Service.

Main FastAPI application entry point.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.api.rapidapi.redact import router as rapidapi_router
from app.core.config import settings
from app.core.logging import logger, log_request
from app.models.schemas import HealthResponse, ErrorResponse
from app.services.pii_detector import get_detector


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - load models on startup."""
    logger.info("Starting Masker API...")
    # Pre-load the PII detector to warm up spaCy models
    get_detector()
    logger.info("PII detector initialized")
    yield
    logger.info("Shutting down Masker API...")


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        413: {"model": ErrorResponse, "description": "Request Entity Too Large"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log request metadata without exposing content."""
    start_time = time.perf_counter()
    
    # Get content length from headers (before reading body)
    content_length = int(request.headers.get("content-length", 0))
    
    response = await call_next(request)
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    log_request(
        logger=logger,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        content_length=content_length,
        duration_ms=duration_ms
    )
    
    return response


@app.middleware("http")
async def size_limit_middleware(request: Request, call_next):
    """Reject requests that exceed the maximum allowed payload size."""
    content_length = int(request.headers.get("content-length", 0))
    
    if content_length > settings.max_payload_size:
        return JSONResponse(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            content={
                "detail": f"Request body too large. Maximum allowed payload size is {settings.max_payload_size} bytes ({settings.max_payload_size // 1024}KB)."
            }
        )
    
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with clean messages."""
    errors = exc.errors()
    
    # Extract first error message for simplicity
    if errors:
        first_error = errors[0]
        loc = " -> ".join(str(l) for l in first_error.get("loc", []))
        msg = first_error.get("msg", "Validation error")
        detail = f"{loc}: {msg}" if loc else msg
    else:
        detail = "Validation error"
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": detail}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions without exposing details."""
    logger.exception("Unexpected error processing request")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint"
)
async def health_check() -> HealthResponse:
    """Check if the service is running."""
    return HealthResponse(
        status="ok",
        version=settings.api_version
    )


# Include API v1 routes
app.include_router(v1_router, prefix="/api/v1")

# Include RapidAPI facade routes
app.include_router(rapidapi_router)

