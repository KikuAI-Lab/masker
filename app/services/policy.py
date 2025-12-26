"""Policy management service.

Loads and applies redaction policies from YAML configuration files.
"""

# import os  # unused
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Literal

import yaml

from app.core.config import settings


class RedactionAction(str, Enum):
    """Possible actions for a PII category."""

    MASK = "mask"  # Replace with ***
    PLACEHOLDER = "placeholder"  # Replace with <TYPE>
    HASH = "hash"  # Replace with SHA256 hash prefix
    DROP = "drop"  # Remove entirely
    KEEP = "keep"  # Do not redact


@dataclass
class Policy:
    """Represents a redaction policy configuration."""

    id: str
    version: int = 1
    categories: dict[str, RedactionAction] = field(default_factory=dict)
    fail_mode: Literal["open", "closed"] = "closed"
    json_denylist_paths: list[str] = field(default_factory=list)
    json_allowlist_paths: list[str] = field(default_factory=list)
    regex_allow: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, policy_id: str, data: dict) -> "Policy":
        """Create a Policy from a dictionary (parsed YAML)."""
        categories = {}
        for cat, action in data.get("categories", {}).items():
            try:
                categories[cat.upper()] = RedactionAction(action)
            except ValueError:
                categories[cat.upper()] = RedactionAction.MASK

        return cls(
            id=policy_id,
            version=data.get("version", 1),
            categories=categories,
            fail_mode=data.get("fail_mode", "closed"),
            json_denylist_paths=data.get("json_rules", {}).get("denylist_paths", []),
            json_allowlist_paths=data.get("json_rules", {}).get("allowlist_paths", []),
            regex_allow=data.get("exceptions", {}).get("regex_allow", []),
        )

    def get_action(self, entity_type: str) -> RedactionAction:
        """Get the redaction action for an entity type.

        Args:
            entity_type: The PII entity type (EMAIL, PHONE, etc.)

        Returns:
            The configured action, or MASK as default.
        """
        return self.categories.get(entity_type.upper(), RedactionAction.MASK)


# Default policy when no config file exists
DEFAULT_POLICY = Policy(
    id="default",
    version=1,
    categories={
        "EMAIL": RedactionAction.MASK,
        "PHONE": RedactionAction.MASK,
        "CARD": RedactionAction.DROP,
        "PERSON": RedactionAction.PLACEHOLDER,
    },
    fail_mode="closed",
)


class PolicyService:
    """Service for loading and managing redaction policies."""

    def __init__(self, policies_dir: str | None = None) -> None:
        """Initialize the policy service.

        Args:
            policies_dir: Directory containing policy YAML files.
        """
        self._policies_dir = Path(policies_dir or settings.policies_dir)
        self._policies: dict[str, Policy] = {}
        self._load_policies()

    def _load_policies(self) -> None:
        """Load all policies from the policies directory."""
        if not self._policies_dir.exists():
            return

        for yaml_file in self._policies_dir.glob("*.yaml"):
            try:
                policy_id = yaml_file.stem
                with open(yaml_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        self._policies[policy_id] = Policy.from_dict(policy_id, data)
            except Exception:
                # Skip invalid policy files
                pass

    def get(self, policy_id: str) -> Policy:
        """Get a policy by ID.

        Args:
            policy_id: The policy identifier.

        Returns:
            The policy if found, otherwise the default policy.
        """
        return self._policies.get(policy_id, DEFAULT_POLICY)

    def list_policies(self) -> list[str]:
        """List all available policy IDs."""
        return list(self._policies.keys())

    @property
    def default_policy(self) -> Policy:
        """Get the default policy."""
        return self.get(settings.default_policy_id)


# Global service instance (singleton)
_service: PolicyService | None = None


def get_policy_service() -> PolicyService:
    """Get or create the global PolicyService instance."""
    global _service
    if _service is None:
        _service = PolicyService()
    return _service


def reset_policy_service() -> None:
    """Reset the service (for testing)."""
    global _service
    _service = None
