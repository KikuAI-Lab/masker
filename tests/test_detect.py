"""Tests for /detect endpoint."""

import pytest
from fastapi.testclient import TestClient


class TestDetectEndpoint:
    """Tests for the /api/v1/detect endpoint."""
    
    def test_detect_email(self, client: TestClient):
        """Should detect email addresses."""
        response = client.post(
            "/api/v1/detect",
            json={"text": "Contact me at test@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["entities"]) >= 1
        email_entity = next(
            (e for e in data["entities"] if e["type"] == "EMAIL"),
            None
        )
        assert email_entity is not None
        assert email_entity["value"] == "test@example.com"
    
    def test_detect_phone_international(self, client: TestClient):
        """Should detect international phone numbers."""
        response = client.post(
            "/api/v1/detect",
            json={"text": "Call +1-555-123-4567 or +7 999 123 45 67"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        phone_entities = [e for e in data["entities"] if e["type"] == "PHONE"]
        assert len(phone_entities) >= 1
    
    def test_detect_card_number(self, client: TestClient):
        """Should detect credit card numbers."""
        response = client.post(
            "/api/v1/detect",
            json={"text": "Card: 4111-1111-1111-1111"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        card_entity = next(
            (e for e in data["entities"] if e["type"] == "CARD"),
            None
        )
        assert card_entity is not None
        assert "4111" in card_entity["value"]
    
    def test_detect_card_number_no_separators(self, client: TestClient):
        """Should detect card numbers without separators."""
        response = client.post(
            "/api/v1/detect",
            json={"text": "Card: 4111111111111111"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        card_entity = next(
            (e for e in data["entities"] if e["type"] == "CARD"),
            None
        )
        assert card_entity is not None
    
    def test_detect_multiple_entities(self, client: TestClient):
        """Should detect multiple PII entities."""
        response = client.post(
            "/api/v1/detect",
            json={
                "text": "Email: user@test.org, Phone: +44 20 7946 0958, Card: 5500 0000 0000 0004"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        types = {e["type"] for e in data["entities"]}
        assert "EMAIL" in types
        assert "CARD" in types
    
    def test_detect_no_pii(self, client: TestClient):
        """Should return empty list when no PII found."""
        response = client.post(
            "/api/v1/detect",
            json={"text": "This text contains no personal information."}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # May have some false positives, but shouldn't have EMAIL/CARD
        email_entities = [e for e in data["entities"] if e["type"] == "EMAIL"]
        card_entities = [e for e in data["entities"] if e["type"] == "CARD"]
        
        assert len(email_entities) == 0
        assert len(card_entities) == 0
    
    def test_detect_empty_text_rejected(self, client: TestClient):
        """Should reject empty text."""
        response = client.post(
            "/api/v1/detect",
            json={"text": ""}
        )
        
        assert response.status_code == 400
    
    def test_detect_missing_text_rejected(self, client: TestClient):
        """Should reject request without text field."""
        response = client.post(
            "/api/v1/detect",
            json={"language": "en"}
        )
        
        assert response.status_code == 400
    
    def test_detect_with_language_ru(self, client: TestClient):
        """Should accept Russian language parameter."""
        response = client.post(
            "/api/v1/detect",
            json={"text": "Email: test@example.ru", "language": "ru"}
        )
        
        assert response.status_code == 200
    
    def test_detect_entity_positions(self, client: TestClient):
        """Should return correct positions for entities."""
        text = "Email: test@example.com"
        response = client.post(
            "/api/v1/detect",
            json={"text": text}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        email_entity = next(
            (e for e in data["entities"] if e["type"] == "EMAIL"),
            None
        )
        assert email_entity is not None
        
        # Verify position is correct
        start = email_entity["start"]
        end = email_entity["end"]
        assert text[start:end] == email_entity["value"]

