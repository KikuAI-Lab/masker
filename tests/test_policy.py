"""Tests for policy management service."""

import tempfile
from pathlib import Path

import pytest

from app.services.policy import (
    Policy,
    PolicyService,
    RedactionAction,
    DEFAULT_POLICY,
    get_policy_service,
    reset_policy_service,
)


class TestRedactionAction:
    """Tests for RedactionAction enum."""
    
    def test_all_actions_defined(self):
        """All expected actions should be defined."""
        assert RedactionAction.MASK.value == "mask"
        assert RedactionAction.PLACEHOLDER.value == "placeholder"
        assert RedactionAction.HASH.value == "hash"
        assert RedactionAction.DROP.value == "drop"
        assert RedactionAction.KEEP.value == "keep"


class TestPolicy:
    """Tests for Policy dataclass."""
    
    def test_from_dict_basic(self):
        """Should create policy from basic dict."""
        data = {
            "version": 1,
            "categories": {
                "email": "mask",
                "phone": "drop",
            },
            "fail_mode": "open",
        }
        
        policy = Policy.from_dict("test", data)
        
        assert policy.id == "test"
        assert policy.version == 1
        assert policy.get_action("EMAIL") == RedactionAction.MASK
        assert policy.get_action("PHONE") == RedactionAction.DROP
        assert policy.fail_mode == "open"
    
    def test_get_action_default_mask(self):
        """Unknown entity types should default to MASK."""
        policy = Policy(id="test")
        assert policy.get_action("UNKNOWN") == RedactionAction.MASK
    
    def test_from_dict_invalid_action(self):
        """Invalid action should fallback to MASK."""
        data = {
            "categories": {
                "email": "invalid_action",
            }
        }
        
        policy = Policy.from_dict("test", data)
        assert policy.get_action("EMAIL") == RedactionAction.MASK


class TestPolicyService:
    """Tests for PolicyService."""
    
    def setup_method(self):
        """Reset service before each test."""
        reset_policy_service()
    
    def test_default_policy_when_no_dir(self):
        """Should return default policy when policies dir doesn't exist."""
        service = PolicyService(policies_dir="/nonexistent/path")
        policy = service.get("anything")
        
        assert policy.id == DEFAULT_POLICY.id
    
    def test_load_policy_from_yaml(self):
        """Should load policy from YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_file = Path(tmpdir) / "strict.yaml"
            policy_file.write_text("""
version: 2
categories:
  email: drop
  phone: drop
  card: drop
  person: mask
fail_mode: closed
""")
            
            service = PolicyService(policies_dir=tmpdir)
            policy = service.get("strict")
            
            assert policy.id == "strict"
            assert policy.version == 2
            assert policy.get_action("EMAIL") == RedactionAction.DROP
            assert policy.fail_mode == "closed"
    
    def test_list_policies(self):
        """Should list all loaded policy IDs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "one.yaml").write_text("version: 1\n")
            (Path(tmpdir) / "two.yaml").write_text("version: 1\n")
            
            service = PolicyService(policies_dir=tmpdir)
            policies = service.list_policies()
            
            assert "one" in policies
            assert "two" in policies
