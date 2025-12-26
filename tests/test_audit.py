"""Tests for audit logging service."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from app.services.audit import (
    AuditEntry,
    AuditLogger,
    get_audit_logger,
    reset_audit_logger,
)


class TestAuditEntry:
    """Tests for AuditEntry dataclass."""
    
    def test_to_dict_excludes_none(self):
        """Should exclude None values from dict."""
        entry = AuditEntry(
            request_id="test-123",
            timestamp="2025-01-01T00:00:00Z",
            tenant_id="tenant1",
            endpoint="/v1/chat/completions",
            entities_total=5,
            entities_by_type={"EMAIL": 2, "PERSON": 3},
            policy_id="default",
            fail_mode="closed",
            redaction_ms=10.5,
            upstream_ms=None,  # Should be excluded
            upstream_status=None,  # Should be excluded
        )
        
        d = entry.to_dict()
        
        assert "request_id" in d
        assert "upstream_ms" not in d
        assert "upstream_status" not in d
    
    def test_to_dict_includes_all_values(self):
        """Should include all non-None values."""
        entry = AuditEntry(
            request_id="test-123",
            timestamp="2025-01-01T00:00:00Z",
            tenant_id="tenant1",
            endpoint="/v1/chat/completions",
            entities_total=5,
            entities_by_type={"EMAIL": 2},
            policy_id="default",
            fail_mode="closed",
            redaction_ms=10.5,
            upstream_ms=100.0,
            upstream_status=200,
            total_ms=115.0,
        )
        
        d = entry.to_dict()
        
        assert d["upstream_ms"] == 100.0
        assert d["upstream_status"] == 200
        assert d["total_ms"] == 115.0


class TestAuditLogger:
    """Tests for AuditLogger."""
    
    def setup_method(self):
        """Reset logger before each test."""
        reset_audit_logger()
    
    def test_log_creates_file(self, monkeypatch):
        """Should create log file when writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock settings
            from app.core.config import Settings
            settings = Settings(audit_dir=tmpdir, audit_enabled=True)
            monkeypatch.setattr("app.services.audit.settings", settings)
            
            logger = AuditLogger(audit_dir=tmpdir)
            
            entry = AuditEntry(
                request_id="test-123",
                timestamp="2025-01-01T00:00:00Z",
                tenant_id="tenant1",
                endpoint="/test",
                entities_total=1,
                entities_by_type={"EMAIL": 1},
                policy_id="default",
                fail_mode="closed",
                redaction_ms=5.0,
            )
            
            logger.log(entry)
            
            # Check file was created
            files = list(Path(tmpdir).glob("*.jsonl"))
            assert len(files) == 1
            
            # Check content
            content = files[0].read_text()
            data = json.loads(content.strip())
            assert data["request_id"] == "test-123"
            assert data["entities_total"] == 1
    
    def test_log_request_helper(self, monkeypatch):
        """log_request should create proper entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from app.core.config import Settings
            settings = Settings(audit_dir=tmpdir, audit_enabled=True)
            monkeypatch.setattr("app.services.audit.settings", settings)
            
            logger = AuditLogger(audit_dir=tmpdir)
            
            logger.log_request(
                request_id="req-456",
                endpoint="/v1/chat/completions",
                entities_by_type={"PERSON": 2, "EMAIL": 1},
                policy_id="strict",
                fail_mode="open",
                redaction_ms=25.5,
                tenant_id="my_tenant",
            )
            
            files = list(Path(tmpdir).glob("*.jsonl"))
            content = files[0].read_text()
            data = json.loads(content.strip())
            
            assert data["endpoint"] == "/v1/chat/completions"
            assert data["entities_total"] == 3
            assert data["tenant_id"] == "my_tenant"
    
    def test_disabled_does_not_write(self, monkeypatch):
        """Should not write when audit_enabled=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from app.core.config import Settings
            settings = Settings(audit_dir=tmpdir, audit_enabled=False)
            monkeypatch.setattr("app.services.audit.settings", settings)
            
            logger = AuditLogger(audit_dir=tmpdir)
            
            entry = AuditEntry(
                request_id="test",
                timestamp="2025-01-01T00:00:00Z",
                tenant_id=None,
                endpoint="/test",
                entities_total=0,
                entities_by_type={},
                policy_id="default",
                fail_mode="closed",
                redaction_ms=1.0,
            )
            
            logger.log(entry)
            
            files = list(Path(tmpdir).glob("*.jsonl"))
            assert len(files) == 0
