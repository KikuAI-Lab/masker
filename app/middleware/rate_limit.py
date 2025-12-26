"""Rate limiting middleware for API protection.

Implements token bucket algorithm with in-memory storage.
For production, consider using Redis for distributed rate limiting.
"""

import time

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.logging import logger


class TokenBucket:
    """Token bucket for rate limiting."""

    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> tuple[bool, float]:
        """Try to consume tokens.

        Returns:
            Tuple of (success, retry_after_seconds)
        """
        now = time.time()
        elapsed = now - self.last_refill

        # Refill tokens based on time elapsed
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, 0.0
        else:
            # Calculate retry after
            tokens_needed = tokens - self.tokens
            retry_after = tokens_needed / self.refill_rate
            return False, retry_after


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using token bucket algorithm.

    Limits:
    - Per IP: 60 requests per minute
    - Global: 1000 requests per minute
    """

    # In-memory storage (use Redis for production)
    _buckets: dict[str, TokenBucket] = {}
    _global_bucket: TokenBucket = None

    # Rate limit settings
    PER_IP_CAPACITY = 60  # requests
    PER_IP_REFILL_RATE = 1.0  # requests per second (60/min)
    GLOBAL_CAPACITY = 1000
    GLOBAL_REFILL_RATE = 16.67  # ~1000/min

    # Cleanup settings
    CLEANUP_INTERVAL = 300  # 5 minutes
    BUCKET_TTL = 600  # 10 minutes
    _last_cleanup = time.time()

    def __init__(self, app):
        super().__init__(app)
        if RateLimitMiddleware._global_bucket is None:
            RateLimitMiddleware._global_bucket = TokenBucket(
                self.GLOBAL_CAPACITY,
                self.GLOBAL_REFILL_RATE
            )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request.

        Security Note: We rely on request.client.host which is set by Uvicorn.
        If behind a proxy (like Nginx/AWS LB), Uvicorn must be started with
        --proxy-headers and --forwarded-allow-ips to securely parse
        X-Forwarded-For. We do NOT manually parse X-Forwarded-For here
        to avoid IP spoofing vulnerabilities.
        """
        # Fall back to direct connection
        if request.client:
            return request.client.host

        return "unknown"

    def _get_or_create_bucket(self, client_ip: str) -> TokenBucket:
        """Get or create token bucket for client IP."""
        if client_ip not in self._buckets:
            self._buckets[client_ip] = TokenBucket(
                self.PER_IP_CAPACITY,
                self.PER_IP_REFILL_RATE
            )
        return self._buckets[client_ip]

    def _cleanup_old_buckets(self):
        """Remove inactive buckets to prevent memory leak."""
        now = time.time()
        if now - self._last_cleanup < self.CLEANUP_INTERVAL:
            return

        # Remove buckets that haven't been used recently
        inactive_keys = [
            ip for ip, bucket in self._buckets.items()
            if now - bucket.last_refill > self.BUCKET_TTL
        ]

        for ip in inactive_keys:
            del self._buckets[ip]

        self._last_cleanup = now

        if inactive_keys:
            logger.info(f"Cleaned up {len(inactive_keys)} inactive rate limit buckets")

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        # Check global rate limit
        global_allowed, global_retry = self._global_bucket.consume(1)
        if not global_allowed:
            logger.warning(f"Global rate limit exceeded, retry after {global_retry:.2f}s")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Global rate limit exceeded. Please try again later.",
                    "retry_after": int(global_retry) + 1
                },
                headers={
                    "Retry-After": str(int(global_retry) + 1),
                    "X-RateLimit-Limit": str(self.GLOBAL_CAPACITY),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + global_retry))
                }
            )

        # Check per-IP rate limit
        ip_bucket = self._get_or_create_bucket(client_ip)
        ip_allowed, ip_retry = ip_bucket.consume(1)

        if not ip_allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip}, retry after {ip_retry:.2f}s")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded for your IP. Max {self.PER_IP_CAPACITY} requests per minute.",
                    "retry_after": int(ip_retry) + 1
                },
                headers={
                    "Retry-After": str(int(ip_retry) + 1),
                    "X-RateLimit-Limit": str(self.PER_IP_CAPACITY),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + ip_retry))
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining_tokens = int(ip_bucket.tokens)
        response.headers["X-RateLimit-Limit"] = str(self.PER_IP_CAPACITY)
        response.headers["X-RateLimit-Remaining"] = str(remaining_tokens)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))

        # Periodic cleanup
        self._cleanup_old_buckets()

        return response
