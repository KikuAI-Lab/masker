"""API Key validation service.

Simple API key validation for multi-tenant authentication.
Keys are loaded from environment variable MASKER_API_KEYS.
"""

from app.core.config import settings


class APIKeyService:
    """Service for validating API keys and extracting tenant IDs."""

    def __init__(self) -> None:
        """Initialize the service and load keys from config."""
        self._keys: dict[str, str] = {}
        self._load_keys()

    def _load_keys(self) -> None:
        """Load API keys from configuration.

        Format: "key1:tenant1,key2:tenant2"
        """
        if not settings.api_keys:
            return

        for pair in settings.api_keys.split(","):
            pair = pair.strip()
            if ":" not in pair:
                continue
            key, tenant_id = pair.split(":", 1)
            self._keys[key.strip()] = tenant_id.strip()

    def validate(self, api_key: str) -> str | None:
        """Validate an API key and return the tenant ID.

        Args:
            api_key: The API key to validate.

        Returns:
            Tenant ID if valid, None otherwise.
        """
        return self._keys.get(api_key)

    def is_enabled(self) -> bool:
        """Check if API key authentication is enabled.

        Returns:
            True if at least one API key is configured.
        """
        return len(self._keys) > 0

    @property
    def key_count(self) -> int:
        """Get the number of configured API keys."""
        return len(self._keys)


# Global service instance (singleton)
_service: APIKeyService | None = None


def get_api_key_service() -> APIKeyService:
    """Get or create the global APIKeyService instance."""
    global _service
    if _service is None:
        _service = APIKeyService()
    return _service


def reset_api_key_service() -> None:
    """Reset the service (for testing)."""
    global _service
    _service = None
