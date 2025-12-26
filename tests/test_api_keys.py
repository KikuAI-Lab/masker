"""Tests for API key validation service."""


from app.services.api_keys import APIKeyService, reset_api_key_service


class TestAPIKeyService:
    """Tests for APIKeyService."""

    def setup_method(self):
        """Reset service before each test."""
        reset_api_key_service()

    def test_empty_keys_disabled(self, monkeypatch):
        """Service should be disabled when no keys configured."""
        monkeypatch.setenv("MASKER_API_KEYS", "")
        reset_api_key_service()

        from app.core.config import Settings

        settings = Settings()
        monkeypatch.setattr("app.services.api_keys.settings", settings)

        service = APIKeyService()
        assert not service.is_enabled()
        assert service.key_count == 0

    def test_parse_single_key(self, monkeypatch):
        """Should parse single key:tenant pair."""
        monkeypatch.setenv("MASKER_API_KEYS", "sk-abc123:tenant1")

        from app.core.config import Settings

        settings = Settings()
        monkeypatch.setattr("app.services.api_keys.settings", settings)

        service = APIKeyService()
        assert service.is_enabled()
        assert service.key_count == 1
        assert service.validate("sk-abc123") == "tenant1"

    def test_parse_multiple_keys(self, monkeypatch):
        """Should parse multiple key:tenant pairs."""
        monkeypatch.setenv("MASKER_API_KEYS", "key1:t1,key2:t2,key3:t3")

        from app.core.config import Settings

        settings = Settings()
        monkeypatch.setattr("app.services.api_keys.settings", settings)

        service = APIKeyService()
        assert service.key_count == 3
        assert service.validate("key1") == "t1"
        assert service.validate("key2") == "t2"
        assert service.validate("key3") == "t3"

    def test_invalid_key_returns_none(self, monkeypatch):
        """Should return None for invalid keys."""
        monkeypatch.setenv("MASKER_API_KEYS", "valid-key:tenant1")

        from app.core.config import Settings

        settings = Settings()
        monkeypatch.setattr("app.services.api_keys.settings", settings)

        service = APIKeyService()
        assert service.validate("invalid-key") is None
        assert service.validate("") is None

    def test_whitespace_handling(self, monkeypatch):
        """Should handle whitespace in key config."""
        monkeypatch.setenv("MASKER_API_KEYS", " key1:tenant1 , key2:tenant2 ")

        from app.core.config import Settings

        settings = Settings()
        monkeypatch.setattr("app.services.api_keys.settings", settings)

        service = APIKeyService()
        assert service.key_count == 2
        assert service.validate("key1") == "tenant1"
        assert service.validate("key2") == "tenant2"
