"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Reset rate limit buckets before each test."""
    from app.middleware.rate_limit import RateLimitMiddleware, TokenBucket

    # Reset per-IP buckets
    RateLimitMiddleware._buckets = {}

    # Reset global bucket
    RateLimitMiddleware._global_bucket = TokenBucket(
        RateLimitMiddleware.GLOBAL_CAPACITY, RateLimitMiddleware.GLOBAL_REFILL_RATE
    )
