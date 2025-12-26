"""Tests for payload size limits."""

from fastapi.testclient import TestClient

from app.core.config import settings


class TestPayloadLimits:
    """Tests for request size limits."""

    def test_text_within_limit(self, client: TestClient):
        """Should accept text within size limit."""
        # Create text just under the limit
        text = "a" * (settings.max_text_size - 100)

        response = client.post("/api/v1/detect", json={"text": text})

        # Should succeed (even if no PII found)
        assert response.status_code == 200

    def test_text_exceeds_limit(self, client: TestClient):
        """Should reject text exceeding size limit."""
        # Create text over the limit
        text = "a" * (settings.max_text_size + 1000)

        response = client.post("/api/v1/detect", json={"text": text})

        # Should be rejected
        assert response.status_code == 400

    def test_payload_exceeds_limit(self, client: TestClient):
        """Should reject payload exceeding max_payload_size."""
        # Create JSON payload over the limit
        large_data = {"key": "x" * (settings.max_payload_size + 1000)}

        response = client.post("/api/v1/detect", json={"json": large_data})

        # Should be rejected (either by middleware or validation)
        assert response.status_code in (400, 413)

    def test_error_message_is_human_readable(self, client: TestClient):
        """Should return human-readable error message."""
        text = "a" * (settings.max_text_size + 1000)

        response = client.post("/api/v1/detect", json={"text": text})

        assert response.status_code in (400, 413)
        data = response.json()
        assert "detail" in data
        # Error should mention size/length/characters
        assert any(
            word in data["detail"].lower()
            for word in ["size", "length", "long", "large", "max", "characters"]
        )

    def test_json_within_limit(self, client: TestClient):
        """Should accept JSON within size limit."""
        # Create JSON with reasonable size
        json_data = {"users": [{"email": f"user{i}@example.com"} for i in range(10)]}

        response = client.post("/api/v1/mask", json={"json": json_data})

        assert response.status_code == 200

    def test_rapidapi_text_limit(self, client: TestClient):
        """Should apply limits to RapidAPI endpoint."""
        text = "a" * (settings.max_text_size + 1000)

        response = client.post("/v1/redact", json={"text": text})

        assert response.status_code in (400, 413)

    def test_rapidapi_json_limit(self, client: TestClient):
        """Should apply limits to RapidAPI JSON mode."""
        large_json = {"data": "x" * (settings.max_payload_size + 1000)}

        response = client.post("/v1/redact", json={"json": large_json})

        assert response.status_code in (400, 413)


class TestConfiguredLimits:
    """Tests to verify configured limits are applied."""

    def test_max_text_size_is_reasonable(self):
        """Verify max_text_size is set to expected value."""
        assert settings.max_text_size == 32 * 1024  # 32KB

    def test_max_payload_size_is_reasonable(self):
        """Verify max_payload_size is set to expected value."""
        assert settings.max_payload_size == 64 * 1024  # 64KB

    def test_payload_size_larger_than_text_size(self):
        """Payload limit should be larger than text limit."""
        assert settings.max_payload_size > settings.max_text_size
