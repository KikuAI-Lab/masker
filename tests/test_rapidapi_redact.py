"""Tests for RapidAPI /v1/redact endpoint."""

import pytest
from fastapi.testclient import TestClient


class TestRapidAPIRedactEndpoint:
    """Tests for the /v1/redact endpoint."""
    
    def test_redact_person_and_email_placeholder_mode(self, client: TestClient):
        """Should redact PERSON and EMAIL with placeholders."""
        response = client.post(
            "/v1/redact",
            json={
                "text": "Hello, my name is John Doe and my email is john@example.com",
                "language": "en",
                "mode": "placeholder"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check redacted text contains placeholders
        assert "<PERSON>" in data["redacted_text"]
        assert "<EMAIL>" in data["redacted_text"]
        assert "John Doe" not in data["redacted_text"]
        assert "john@example.com" not in data["redacted_text"]
        
        # Check items
        assert len(data["items"]) >= 2
        entity_types = {item["entity_type"] for item in data["items"]}
        assert "PERSON" in entity_types
        assert "EMAIL" in entity_types
        
        # Check scores
        for item in data["items"]:
            assert 0.0 <= item["score"] <= 1.0
        
        # Check processing time
        assert data["processing_time_ms"] >= 0
    
    def test_redact_mask_mode(self, client: TestClient):
        """Should redact with *** in mask mode."""
        response = client.post(
            "/v1/redact",
            json={
                "text": "Contact me at test@example.com",
                "mode": "mask"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check redacted text contains mask
        assert "***" in data["redacted_text"]
        assert "test@example.com" not in data["redacted_text"]
        
        # Email should be detected
        email_items = [i for i in data["items"] if i["entity_type"] == "EMAIL"]
        assert len(email_items) == 1
        assert email_items[0]["score"] == 1.0  # Regex detection
    
    def test_redact_placeholder_mode(self, client: TestClient):
        """Should redact with <TYPE> placeholders."""
        response = client.post(
            "/v1/redact",
            json={
                "text": "Card number: 4111-1111-1111-1111",
                "mode": "placeholder"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check redacted text contains placeholder
        assert "<CARD>" in data["redacted_text"]
        assert "4111-1111-1111-1111" not in data["redacted_text"]
    
    def test_redact_filter_entities_only_email(self, client: TestClient):
        """Should redact only specified entity types."""
        response = client.post(
            "/v1/redact",
            json={
                "text": "John Doe's email is john@example.com",
                "entities": ["EMAIL"],
                "mode": "placeholder"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # PERSON should NOT be redacted (not in filter)
        assert "John Doe" in data["redacted_text"]
        
        # EMAIL should be redacted
        assert "<EMAIL>" in data["redacted_text"]
        assert "john@example.com" not in data["redacted_text"]
        
        # Only EMAIL in items
        entity_types = {item["entity_type"] for item in data["items"]}
        assert entity_types == {"EMAIL"}
    
    def test_redact_filter_entities_only_person(self, client: TestClient):
        """Should leave email intact when only PERSON is filtered."""
        response = client.post(
            "/v1/redact",
            json={
                "text": "John Doe's email is john@example.com",
                "entities": ["PERSON"],
                "mode": "placeholder"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # EMAIL should NOT be redacted
        assert "john@example.com" in data["redacted_text"]
        
        # PERSON should be redacted
        assert "<PERSON>" in data["redacted_text"]
        assert "John Doe" not in data["redacted_text"]
    
    def test_redact_multiple_entities_same_type(self, client: TestClient):
        """Should handle multiple entities of the same type."""
        response = client.post(
            "/v1/redact",
            json={
                "text": "Contact us at info@company.com or support@company.com",
                "mode": "mask"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Both emails should be masked
        assert "info@company.com" not in data["redacted_text"]
        assert "support@company.com" not in data["redacted_text"]
        
        # Should have 2 EMAIL items
        email_items = [i for i in data["items"] if i["entity_type"] == "EMAIL"]
        assert len(email_items) == 2
    
    def test_redact_no_pii(self, client: TestClient):
        """Should return original text when no PII found."""
        original = "Hello, this is a test message."
        response = client.post(
            "/v1/redact",
            json={"text": original}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Text unchanged
        assert data["redacted_text"] == original
        assert data["items"] == []
        assert data["processing_time_ms"] >= 0
    
    def test_redact_default_mode_is_mask(self, client: TestClient):
        """Should use mask mode by default."""
        response = client.post(
            "/v1/redact",
            json={"text": "Email: user@test.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Default mode is mask
        assert "***" in data["redacted_text"]
        assert "<EMAIL>" not in data["redacted_text"]
    
    def test_redact_default_language_is_en(self, client: TestClient):
        """Should use English by default."""
        response = client.post(
            "/v1/redact",
            json={"text": "John Smith at john@test.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect PERSON with English NER
        entity_types = {item["entity_type"] for item in data["items"]}
        assert "EMAIL" in entity_types
    
    def test_redact_russian_language(self, client: TestClient):
        """Should handle Russian text."""
        response = client.post(
            "/v1/redact",
            json={
                "text": "Иван Петров: ivan@mail.ru",
                "language": "ru",
                "mode": "placeholder"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect email
        assert "<EMAIL>" in data["redacted_text"]
        assert "ivan@mail.ru" not in data["redacted_text"]
    
    def test_redact_response_has_processing_time(self, client: TestClient):
        """Should include processing time in response."""
        response = client.post(
            "/v1/redact",
            json={"text": "Test text"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "processing_time_ms" in data
        assert isinstance(data["processing_time_ms"], (int, float))
        assert data["processing_time_ms"] >= 0
    
    def test_redact_items_have_correct_structure(self, client: TestClient):
        """Should return items with correct structure."""
        response = client.post(
            "/v1/redact",
            json={"text": "Contact: test@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) >= 1
        item = data["items"][0]
        
        # Check all required fields
        assert "entity_type" in item
        assert "start" in item
        assert "end" in item
        assert "score" in item
        
        # Check types
        assert isinstance(item["entity_type"], str)
        assert isinstance(item["start"], int)
        assert isinstance(item["end"], int)
        assert isinstance(item["score"], float)
    
    def test_redact_empty_entities_filter_redacts_all(self, client: TestClient):
        """Empty entities list should be treated as None (redact all)."""
        response = client.post(
            "/v1/redact",
            json={
                "text": "John Doe at john@test.com",
                "entities": None,
                "mode": "mask"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Both should be redacted
        assert "John Doe" not in data["redacted_text"]
        assert "john@test.com" not in data["redacted_text"]
    
    def test_redact_invalid_mode_rejected(self, client: TestClient):
        """Should reject invalid mode."""
        response = client.post(
            "/v1/redact",
            json={
                "text": "Test",
                "mode": "invalid"
            }
        )
        
        assert response.status_code == 400
    
    def test_redact_empty_text_rejected(self, client: TestClient):
        """Should reject empty text."""
        response = client.post(
            "/v1/redact",
            json={"text": ""}
        )
        
        assert response.status_code == 400

