# Masker API - Test Examples

This directory contains example tests showing how to use Masker API.

## Running Tests

```bash
# Install dependencies
pip install pytest requests

# Run tests
pytest tests/
```

## Test Files

- `test_health.py` - Health check endpoint tests
- `conftest.py` - Pytest configuration

## Example Test

```python
import pytest
import requests

def test_health_check():
    """Test that health endpoint returns OK."""
    response = requests.get("https://masker.kikuai.dev/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
```

## Integration Tests

These tests can be run against the live API to verify functionality:

```bash
# Test against live API
pytest tests/ -v --api-url=https://masker.kikuai.dev
```

