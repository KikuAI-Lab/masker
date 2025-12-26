
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)

def test_ip_spoofing_rate_limit_bypass_fixed(client):
    """
    Test that an attacker CANNOT bypass rate limits by spoofing X-Forwarded-For.

    This test demonstrates the fix:
    1. Exhaust the rate limit for one "IP" (the real client IP).
    2. Try to change the spoofed X-Forwarded-For header.
    3. Verify we are STILL blocked (429), meaning the app ignored the spoofed header.
    """

    spoofed_ip_1 = "203.0.113.1"
    headers_1 = {"X-Forwarded-For": spoofed_ip_1}

    # Send one request to make sure it works
    response = client.post(
        "/v1/detect",
        json={"text": "Hello world"},
        headers=headers_1
    )
    # Note: If tests run in parallel or share state, this might already be 429.
    # But we assume isolation or clean state.
    # Wait, the TokenBucket is in-memory global variable in RateLimitMiddleware class.
    # It is NOT reset between tests unless we manually reset it.

    # We should reset the buckets for this test to be reliable.
    from app.middleware.rate_limit import RateLimitMiddleware
    RateLimitMiddleware._buckets = {}
    RateLimitMiddleware._global_bucket = None
    # Re-init global bucket
    from app.middleware.rate_limit import TokenBucket
    RateLimitMiddleware._global_bucket = TokenBucket(
        RateLimitMiddleware.GLOBAL_CAPACITY,
        RateLimitMiddleware.GLOBAL_REFILL_RATE
    )

    # Now try again
    response = client.post(
        "/v1/detect",
        json={"text": "Hello world"},
        headers=headers_1
    )
    assert response.status_code == 200

    # Exhaust the limit (capacity 60).
    # We sent 1. Send 60 more.
    for _ in range(60):
        client.post(
            "/v1/detect",
            json={"text": "Hello world"},
            headers=headers_1
        )

    # The next request should fail with 429
    response = client.post(
        "/v1/detect",
        json={"text": "Hello world"},
        headers=headers_1
    )
    assert response.status_code == 429

    # NOW, the exploit: Change the spoofed IP and try again.
    spoofed_ip_2 = "203.0.113.2"
    headers_2 = {"X-Forwarded-For": spoofed_ip_2}

    response = client.post(
        "/v1/detect",
        json={"text": "Hello world"},
        headers=headers_2
    )

    # If fixed, this MUST be 429, because the app sees the real IP (testclient/127.0.0.1)
    # which is already exhausted. It should ignore X-Forwarded-For.
    assert response.status_code == 429, "Vulnerability persisted: Rate limit bypassed via X-Forwarded-For"
