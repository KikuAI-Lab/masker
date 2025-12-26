"""Audit logging service.

Writes audit logs in JSONL format without storing raw text.
Only metadata and statistics are logged.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.config import settings


@dataclass
class AuditEntry:
    """Represents a single audit log entry."""

    request_id: str
    timestamp: str
    tenant_id: str | None
    endpoint: str
    entities_total: int
    entities_by_type: dict[str, int]
    policy_id: str
    fail_mode: str
    redaction_ms: float
    upstream_ms: float | None = None
    upstream_status: int | None = None
    total_ms: float | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class AuditLogger:
    """JSONL audit logger with daily rotation."""

    def __init__(self, audit_dir: str | None = None) -> None:
        """Initialize the audit logger.

        Args:
            audit_dir: Directory for audit logs. Defaults to settings.audit_dir.
        """
        self._audit_dir = Path(audit_dir or settings.audit_dir)
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Create audit directory if it doesn't exist."""
        self._audit_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_path(self) -> Path:
        """Get the path for today's log file."""
        date_str = datetime.now(datetime.UTC).strftime("%Y-%m-%d")
        return self._audit_dir / f"{date_str}.jsonl"

    def log(self, entry: AuditEntry) -> None:
        """Write an audit entry to the log file.

        Args:
            entry: The audit entry to log.
        """
        if not settings.audit_enabled:
            return

        log_path = self._get_log_path()
        line = json.dumps(entry.to_dict(), ensure_ascii=False)

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def log_request(
        self,
        request_id: str,
        endpoint: str,
        entities_by_type: dict[str, int],
        policy_id: str,
        fail_mode: str,
        redaction_ms: float,
        tenant_id: str | None = None,
        upstream_ms: float | None = None,
        upstream_status: int | None = None,
        total_ms: float | None = None,
        error: str | None = None,
    ) -> None:
        """Log a request with all metadata.

        Args:
            request_id: Unique request identifier.
            endpoint: API endpoint called.
            entities_by_type: Count of entities detected by type.
            policy_id: ID of the policy applied.
            fail_mode: The fail mode setting (open/closed).
            redaction_ms: Time spent on redaction in ms.
            tenant_id: Optional tenant identifier.
            upstream_ms: Optional upstream latency in ms.
            upstream_status: Optional upstream HTTP status.
            total_ms: Optional total request time in ms.
            error: Optional error message.
        """
        entry = AuditEntry(
            request_id=request_id,
            timestamp=datetime.now(datetime.UTC).isoformat(),
            tenant_id=tenant_id,
            endpoint=endpoint,
            entities_total=sum(entities_by_type.values()),
            entities_by_type=entities_by_type,
            policy_id=policy_id,
            fail_mode=fail_mode,
            redaction_ms=round(redaction_ms, 2),
            upstream_ms=round(upstream_ms, 2) if upstream_ms else None,
            upstream_status=upstream_status,
            total_ms=round(total_ms, 2) if total_ms else None,
            error=error,
        )
        self.log(entry)


# Global logger instance (singleton)
_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get or create the global AuditLogger instance."""
    global _logger
    if _logger is None:
        _logger = AuditLogger()
    return _logger


def reset_audit_logger() -> None:
    """Reset the logger (for testing)."""
    global _logger
    _logger = None
