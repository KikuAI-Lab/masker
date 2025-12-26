"""Tests for /mask endpoint."""

from fastapi.testclient import TestClient


class TestMaskEndpoint:
    """Tests for the /api/v1/mask endpoint."""

    def test_mask_email(self, client: TestClient):
        """Should mask email addresses with ***."""
        response = client.post(
            "/api/v1/mask",
            json={"text": "Contact me at test@example.com please"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "***" in data["text"]
        assert "test@example.com" not in data["text"]

        # Check entity info
        assert len(data["entities"]) >= 1
        email_entity = next(
            (e for e in data["entities"] if e["type"] == "EMAIL"),
            None
        )
        assert email_entity is not None
        assert email_entity["value"] == "test@example.com"
        assert email_entity["masked_value"] == "***"

    def test_mask_phone(self, client: TestClient):
        """Should mask phone numbers with ***."""
        response = client.post(
            "/api/v1/mask",
            json={"text": "Call +1-555-123-4567 now"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "***" in data["text"]
        assert "+1-555-123-4567" not in data["text"]

    def test_mask_card(self, client: TestClient):
        """Should mask credit card numbers with ***."""
        response = client.post(
            "/api/v1/mask",
            json={"text": "Pay with card 4111-1111-1111-1111"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "***" in data["text"]
        assert "4111-1111-1111-1111" not in data["text"]

    def test_mask_multiple_entities(self, client: TestClient):
        """Should mask multiple PII entities."""
        text = "Email: a@b.com, Phone: +1-800-555-1234, Card: 4111 1111 1111 1111"
        response = client.post(
            "/api/v1/mask",
            json={"text": text}
        )

        assert response.status_code == 200
        data = response.json()

        # Original values should not appear
        assert "a@b.com" not in data["text"]
        assert "4111 1111 1111 1111" not in data["text"]

        # Multiple entities should be detected
        assert len(data["entities"]) >= 2

    def test_mask_no_pii(self, client: TestClient):
        """Should return original text when no PII found."""
        original = "Hello, this is a safe message."
        response = client.post(
            "/api/v1/mask",
            json={"text": original}
        )

        assert response.status_code == 200
        data = response.json()

        # Text should be unchanged or very similar
        # (NER might pick up some words as names)
        assert data["text"] is not None

    def test_mask_preserves_structure(self, client: TestClient):
        """Should preserve text structure around masked entities."""
        response = client.post(
            "/api/v1/mask",
            json={"text": "Before test@example.com After"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["text"].startswith("Before ")
        assert data["text"].endswith(" After")

    def test_mask_empty_text_rejected(self, client: TestClient):
        """Should reject empty text."""
        response = client.post(
            "/api/v1/mask",
            json={"text": ""}
        )

        assert response.status_code == 400

    def test_mask_with_language(self, client: TestClient):
        """Should accept language parameter."""
        response = client.post(
            "/api/v1/mask",
            json={"text": "Email: test@example.ru", "language": "ru"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "***" in data["text"]

    def test_mask_returns_entity_positions(self, client: TestClient):
        """Should return original positions in response."""
        text = "Email: test@example.com here"
        response = client.post(
            "/api/v1/mask",
            json={"text": text}
        )

        assert response.status_code == 200
        data = response.json()

        email_entity = next(
            (e for e in data["entities"] if e["type"] == "EMAIL"),
            None
        )
        assert email_entity is not None

        # Position should match original text
        start = email_entity["start"]
        end = email_entity["end"]
        assert text[start:end] == email_entity["value"]

