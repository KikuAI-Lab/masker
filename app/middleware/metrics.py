import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION_SECONDS

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.perf_counter() - start_time
            
            # Group endpoints to avoid high cardinality
            path = request.url.path
            if path.startswith("/api/v1/"):
                # Keep specific API paths
                pass
            elif path.startswith("/v1/"):
                pass
            elif path in ["/health", "/metrics", "/docs", "/openapi.json", "/redoc"]:
                pass
            else:
                path = "other"
            
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=path,
                status=status_code
            ).inc()
            
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                endpoint=path
            ).observe(duration)
            
        return response
