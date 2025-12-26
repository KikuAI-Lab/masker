from prometheus_client import Counter, Histogram

# HTTP Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total", "Total number of HTTP requests", ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds", "HTTP request duration in seconds", ["method", "endpoint"]
)

# Business Metrics
PII_DETECTED_TOTAL = Counter(
    "pii_detected_total", "Total number of PII entities detected", ["entity_type"]
)
