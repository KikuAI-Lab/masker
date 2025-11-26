"""Tests for JSON mode in all endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestJsonModeDetect:
    """Tests for /api/v1/detect with JSON input."""
    
    def test_detect_json_simple(self, client: TestClient):
        """Should detect PII in simple JSON object."""
        response = client.post(
            "/api/v1/detect",
            json={
                "json": {
                    "email": "john@example.com",
                    "name": "John Doe"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "entities" in data
        assert len(data["entities"]) >= 1
        
        # Check entity has path
        email_entities = [e for e in data["entities"] if e["type"] == "EMAIL"]
        assert len(email_entities) == 1
        assert email_entities[0]["path"] == "email"
    
    def test_detect_json_nested(self, client: TestClient):
        """Should detect PII in nested JSON structure."""
        response = client.post(
            "/api/v1/detect",
            json={
                "json": {
                    "user": {
                        "profile": {
                            "email": "test@example.com",
                            "phone": "+1-555-123-4567"
                        }
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        paths = {e["path"] for e in data["entities"]}
        assert "user.profile.email" in paths
        assert "user.profile.phone" in paths
    
    def test_detect_json_array(self, client: TestClient):
        """Should detect PII in JSON arrays."""
        response = client.post(
            "/api/v1/detect",
            json={
                "json": {
                    "contacts": [
                        {"email": "a@b.com"},
                        {"email": "c@d.com"}
                    ]
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        email_entities = [e for e in data["entities"] if e["type"] == "EMAIL"]
        assert len(email_entities) == 2
        
        paths = {e["path"] for e in email_entities}
        assert "contacts[0].email" in paths
        assert "contacts[1].email" in paths
    
    def test_detect_json_preserves_non_string_values(self, client: TestClient):
        """Should not process non-string values."""
        response = client.post(
            "/api/v1/detect",
            json={
                "json": {
                    "count": 42,
                    "active": True,
                    "data": None,
                    "email": "test@example.com"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Only email should be detected
        assert len(data["entities"]) >= 1
        entity_types = {e["type"] for e in data["entities"]}
        assert "EMAIL" in entity_types


class TestJsonModeMask:
    """Tests for /api/v1/mask with JSON input."""
    
    def test_mask_json_simple(self, client: TestClient):
        """Should mask PII in simple JSON."""
        response = client.post(
            "/api/v1/mask",
            json={
                "json": {
                    "email": "john@example.com",
                    "message": "Hello world"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "json" in data
        assert data["json"]["email"] == "***"
        assert data["json"]["message"] == "Hello world"  # Unchanged
    
    def test_mask_json_nested(self, client: TestClient):
        """Should mask PII in nested JSON."""
        response = client.post(
            "/api/v1/mask",
            json={
                "json": {
                    "user": {
                        "name": "John Doe",
                        "contact": {
                            "email": "john@example.com"
                        }
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Email should be masked
        assert data["json"]["user"]["contact"]["email"] == "***"
        
        # Structure should be preserved
        assert "user" in data["json"]
        assert "contact" in data["json"]["user"]
    
    def test_mask_json_array(self, client: TestClient):
        """Should mask PII in arrays."""
        response = client.post(
            "/api/v1/mask",
            json={
                "json": {
                    "emails": ["a@b.com", "c@d.com"]
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["json"]["emails"] == ["***", "***"]
    
    def test_mask_json_preserves_structure(self, client: TestClient):
        """Should preserve original JSON structure."""
        original = {
            "string": "test@example.com",
            "number": 42,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        response = client.post(
            "/api/v1/mask",
            json={"json": original}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        result = data["json"]
        assert result["string"] == "***"  # Email masked
        assert result["number"] == 42
        assert result["boolean"] is True
        assert result["null"] is None
        assert result["array"] == [1, 2, 3]
        assert result["nested"] == {"key": "value"}


class TestJsonModeRedact:
    """Tests for /api/v1/redact with JSON input."""
    
    def test_redact_json_simple(self, client: TestClient):
        """Should redact PII in simple JSON."""
        response = client.post(
            "/api/v1/redact",
            json={
                "json": {
                    "card": "4111-1111-1111-1111"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["json"]["card"] == "[REDACTED]"
    
    def test_redact_json_nested(self, client: TestClient):
        """Should redact PII in nested JSON."""
        response = client.post(
            "/api/v1/redact",
            json={
                "json": {
                    "payment": {
                        "card_number": "5500 0000 0000 0004"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["json"]["payment"]["card_number"] == "[REDACTED]"


class TestJsonModeRapidAPI:
    """Tests for /v1/redact RapidAPI endpoint with JSON input."""
    
    def test_rapidapi_json_mask_mode(self, client: TestClient):
        """Should mask PII in JSON with mask mode."""
        response = client.post(
            "/v1/redact",
            json={
                "json": {
                    "user": {"email": "test@example.com"}
                },
                "mode": "mask"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["redacted_json"]["user"]["email"] == "***"
        assert data["redacted_text"] is None
        assert "processing_time_ms" in data
    
    def test_rapidapi_json_placeholder_mode(self, client: TestClient):
        """Should use placeholders in JSON."""
        response = client.post(
            "/v1/redact",
            json={
                "json": {
                    "email": "test@example.com"
                },
                "mode": "placeholder"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["redacted_json"]["email"] == "<EMAIL>"
    
    def test_rapidapi_json_filter_entities(self, client: TestClient):
        """Should filter entities in JSON mode."""
        response = client.post(
            "/v1/redact",
            json={
                "json": {
                    "email": "test@example.com",
                    "phone": "+1-555-123-4567"
                },
                "entities": ["EMAIL"],
                "mode": "mask"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Only email should be masked
        assert data["redacted_json"]["email"] == "***"
        # Phone should remain (not in filter)
        assert data["redacted_json"]["phone"] == "+1-555-123-4567"
    
    def test_rapidapi_json_items_have_path(self, client: TestClient):
        """Should include JSON path in items."""
        response = client.post(
            "/v1/redact",
            json={
                "json": {
                    "user": {"email": "test@example.com"}
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) >= 1
        assert data["items"][0]["path"] == "user.email"


class TestJsonModeValidation:
    """Tests for JSON mode validation."""
    
    def test_cannot_provide_both_text_and_json(self, client: TestClient):
        """Should reject when both text and json provided."""
        response = client.post(
            "/api/v1/detect",
            json={
                "text": "Hello",
                "json": {"key": "value"}
            }
        )
        
        assert response.status_code == 400
    
    def test_must_provide_text_or_json(self, client: TestClient):
        """Should reject when neither text nor json provided."""
        response = client.post(
            "/api/v1/detect",
            json={"language": "en"}
        )
        
        assert response.status_code == 400
    
    def test_text_mode_still_works(self, client: TestClient):
        """Should still support text-only mode."""
        response = client.post(
            "/api/v1/mask",
            json={"text": "Email: test@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "text" in data
        assert "***" in data["text"]


class TestJsonModeComplexStructures:
    """Tests for complex JSON structures."""
    
    def test_deeply_nested_structure(self, client: TestClient):
        """Should handle deeply nested structures."""
        response = client.post(
            "/api/v1/mask",
            json={
                "json": {
                    "level1": {
                        "level2": {
                            "level3": {
                                "level4": {
                                    "email": "deep@example.com"
                                }
                            }
                        }
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["json"]["level1"]["level2"]["level3"]["level4"]["email"] == "***"
    
    def test_mixed_array_and_objects(self, client: TestClient):
        """Should handle mixed arrays and objects."""
        response = client.post(
            "/api/v1/mask",
            json={
                "json": {
                    "users": [
                        {"name": "John Doe", "emails": ["john@a.com", "john@b.com"]},
                        {"name": "Jane Smith", "emails": ["jane@c.com"]}
                    ]
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All emails should be masked
        for user in data["json"]["users"]:
            for email in user["emails"]:
                assert email == "***"
    
    def test_empty_structures(self, client: TestClient):
        """Should handle empty structures."""
        response = client.post(
            "/api/v1/mask",
            json={
                "json": {
                    "empty_object": {},
                    "empty_array": [],
                    "null_value": None
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["json"]["empty_object"] == {}
        assert data["json"]["empty_array"] == []
        assert data["json"]["null_value"] is None
    
    def test_multiple_pii_in_same_field(self, client: TestClient):
        """Should handle multiple PII in same string field."""
        response = client.post(
            "/api/v1/mask",
            json={
                "json": {
                    "message": "Contact john@example.com or jane@example.com"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Both emails should be masked
        assert "john@example.com" not in data["json"]["message"]
        assert "jane@example.com" not in data["json"]["message"]
        assert "***" in data["json"]["message"]

