"""Safe logging configuration.

IMPORTANT: Never log the content of text or JSON fields to protect user privacy.
Only log service metadata: method, path, status, content_length, duration.
"""

import logging
import sys
from typing import Any


def setup_logging() -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger("masker")
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    content_length: int,
    duration_ms: float
) -> None:
    """Log request metadata safely without exposing content.
    
    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: Response status code
        content_length: Size of request body in bytes
        duration_ms: Request processing time in milliseconds
    """
    logger.info(
        "request: method=%s path=%s status=%d content_length=%d duration_ms=%.2f",
        method,
        path,
        status_code,
        content_length,
        duration_ms
    )


def sanitize_for_logging(data: dict[str, Any]) -> dict[str, Any]:
    """Remove sensitive fields from data before logging.
    
    Args:
        data: Dictionary that may contain sensitive fields
        
    Returns:
        Dictionary with sensitive fields replaced by placeholders
    """
    sensitive_fields = {"text", "json", "content", "body"}
    sanitized = {}
    
    for key, value in data.items():
        if key.lower() in sensitive_fields:
            sanitized[key] = "[CONTENT_HIDDEN]"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_logging(value)
        else:
            sanitized[key] = value
    
    return sanitized


# Global logger instance
logger = setup_logging()

