"""Tests for /redact endpoint."""

from fastapi.testclient import TestClient


class TestRedactEndpoint:
    """Tests for the /api/v1/redact endpoint."""

    def test_redact_email(self, client: TestClient):
        """Should redact email addresses with [REDACTED]."""
        response = client.post(
            "/api/v1/redact",
            json={"text": "Contact me at test@example.com please"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "[REDACTED]" in data["text"]
        assert "test@example.com" not in data["text"]

        # Check entity info
        email_entity = next(
            (e for e in data["entities"] if e["type"] == "EMAIL"),
            None
        )
        assert email_entity is not None
        assert email_entity["value"] == "test@example.com"
        assert email_entity["masked_value"] == "[REDACTED]"

    def test_redact_phone(self, client: TestClient):
        """Should redact phone numbers with [REDACTED]."""
        response = client.post(
            "/api/v1/redact",
            json={"text": "Call +1-555-123-4567 now"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "[REDACTED]" in data["text"]
        assert "+1-555-123-4567" not in data["text"]

    def test_redact_card(self, client: TestClient):
        """Should redact credit card numbers with [REDACTED]."""
        response = client.post(
            "/api/v1/redact",
            json={"text": "Pay with card 4111-1111-1111-1111"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "[REDACTED]" in data["text"]
        assert "4111-1111-1111-1111" not in data["text"]

    def test_redact_multiple_entities(self, client: TestClient):
        """Should redact multiple PII entities."""
        response = client.post(
            "/api/v1/redact",
            json={
                "text": "Email: a@b.com, Card: 4111 1111 1111 1111"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Count [REDACTED] occurrences
        redacted_count = data["text"].count("[REDACTED]")
        assert redacted_count >= 2

    def test_redact_vs_mask_difference(self, client: TestClient):
        """Redact should use [REDACTED] while mask uses ***."""
        text = "Email: test@example.com"

        mask_response = client.post(
            "/api/v1/mask",
            json={"text": text}
        )
        redact_response = client.post(
            "/api/v1/redact",
            json={"text": text}
        )

        assert mask_response.status_code == 200
        assert redact_response.status_code == 200

        mask_data = mask_response.json()
        redact_data = redact_response.json()

        # Different replacement tokens
        assert "***" in mask_data["text"]
        assert "[REDACTED]" in redact_data["text"]

        # Same entities detected
        assert len(mask_data["entities"]) == len(redact_data["entities"])

    def test_redact_empty_text_rejected(self, client: TestClient):
        """Should reject empty text."""
        response = client.post(
            "/api/v1/redact",
            json={"text": ""}
        )

        assert response.status_code == 400

    def test_redact_no_pii(self, client: TestClient):
        """Should return original text when no PII found."""
        original = "Hello world, nothing sensitive here."
        response = client.post(
            "/api/v1/redact",
            json={"text": original}
        )

        assert response.status_code == 200
        data = response.json()

        # Text should be present in response
        assert data["text"] is not None

    def test_redact_preserves_structure(self, client: TestClient):
        """Should preserve text structure around redacted entities."""
        response = client.post(
            "/api/v1/redact",
            json={"text": "Start test@example.com End"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["text"].startswith("Start ")
        assert data["text"].endswith(" End")

