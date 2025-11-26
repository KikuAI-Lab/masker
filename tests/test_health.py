"""Tests for health check and error handling."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /health endpoint."""
    
    def test_health_check(self, client: TestClient):
        """Should return ok status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "version" in data


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_invalid_json(self, client: TestClient):
        """Should return 400 for invalid JSON."""
        response = client.post(
            "/api/v1/detect",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in (400, 422)
    
    def test_invalid_language(self, client: TestClient):
        """Should reject invalid language codes."""
        response = client.post(
            "/api/v1/detect",
            json={"text": "Hello", "language": "invalid"}
        )
        
        assert response.status_code == 400
    
    def test_text_too_long(self, client: TestClient):
        """Should reject text that exceeds size limit."""
        # Create text larger than 32KB
        long_text = "a" * (33 * 1024)
        
        response = client.post(
            "/api/v1/detect",
            json={"text": long_text}
        )
        
        # Should be rejected (either by middleware or validation)
        assert response.status_code in (400, 413)
    
    def test_missing_content_type(self, client: TestClient):
        """Should handle missing content type gracefully."""
        response = client.post(
            "/api/v1/detect",
            content='{"text": "hello"}'
        )
        
        # FastAPI should handle this
        assert response.status_code in (200, 400, 422)
    
    def test_404_for_unknown_endpoint(self, client: TestClient):
        """Should return 404 for unknown endpoints."""
        response = client.get("/api/v1/unknown")
        
        assert response.status_code == 404

