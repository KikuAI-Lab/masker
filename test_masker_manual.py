#!/usr/bin/env python3
"""
Manual test script for Masker API - real user testing.
Tests all endpoints as a real user would.
"""

import httpx
import json
from typing import Dict, Any


BASE_URL = "http://127.0.0.1:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print('=' * 80)


def print_result(endpoint: str, status: int, response: Any, error: str = None):
    """Print test result in a formatted way."""
    if error:
        print(f"❌ {endpoint} - FAILED")
        print(f"   Error: {error}")
    elif 200 <= status < 300:
        print(f"✅ {endpoint} - OK (status: {status})")
        print(f"   Response: {json.dumps(response, indent=2, ensure_ascii=False)[:500]}")
    else:
        print(f"⚠️  {endpoint} - Unexpected status {status}")
        print(f"   Response: {json.dumps(response, indent=2, ensure_ascii=False)[:500]}")


def test_health():
    """Test health endpoint."""
    print_section("1. Health Check")
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=10)
        print_result("GET /health", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print_result("GET /health", 0, None, str(e))
        return False


def test_detect_text():
    """Test detect endpoint with text."""
    print_section("2. Detect PII - Text Mode")
    
    test_cases = [
        {
            "name": "English text with email and name",
            "payload": {
                "text": "Hello, my name is John Doe and my email is john.doe@example.com. Call me at +1-555-123-4567."
            }
        },
        {
            "name": "Russian text",
            "payload": {
                "text": "Привет, меня зовут Иван Петров, мой email ivan@mail.ru",
                "language": "ru"
            }
        },
        {
            "name": "Credit card number",
            "payload": {
                "text": "My credit card is 4532-1234-5678-9010"
            }
        },
    ]
    
    success_count = 0
    for case in test_cases:
        print(f"\nTest: {case['name']}")
        try:
            response = httpx.post(f"{BASE_URL}/api/v1/detect", json=case["payload"], timeout=10)
            print_result("POST /api/v1/detect", response.status_code, response.json())
            if response.status_code == 200:
                success_count += 1
        except Exception as e:
            print_result("POST /api/v1/detect", 0, None, str(e))
    
    return success_count == len(test_cases)


def test_detect_json():
    """Test detect endpoint with JSON."""
    print_section("3. Detect PII - JSON Mode")
    
    payload = {
        "json": {
            "user": {
                "name": "Jane Smith",
                "email": "jane.smith@company.com",
                "phone": "+44-20-7123-4567"
            },
            "message": "Please contact me at my office",
            "metadata": {
                "count": 42,
                "active": True
            }
        }
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/api/v1/detect", json=payload, timeout=10)
        print_result("POST /api/v1/detect (JSON)", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print_result("POST /api/v1/detect (JSON)", 0, None, str(e))
        return False


def test_mask_text():
    """Test mask endpoint with text."""
    print_section("4. Mask PII - Text Mode")
    
    payload = {
        "text": "Contact John Doe at john@example.com or +1-555-9876"
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/api/v1/mask", json=payload, timeout=10)
        result = response.json()
        print_result("POST /api/v1/mask", response.status_code, result)
        
        # Check if masking actually happened
        if response.status_code == 200:
            masked_text = result.get("text", "")
            if "***" in masked_text:
                print("✓ Masking with *** confirmed")
                return True
            else:
                print("⚠️ Warning: No *** found in masked text")
                return False
        return False
    except Exception as e:
        print_result("POST /api/v1/mask", 0, None, str(e))
        return False


def test_mask_json():
    """Test mask endpoint with JSON."""
    print_section("5. Mask PII - JSON Mode")
    
    payload = {
        "json": {
            "customer": {
                "name": "Alice Johnson",
                "email": "alice@test.com",
                "age": 30
            }
        }
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/api/v1/mask", json=payload, timeout=10)
        print_result("POST /api/v1/mask (JSON)", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print_result("POST /api/v1/mask (JSON)", 0, None, str(e))
        return False


def test_redact_text():
    """Test redact endpoint with text."""
    print_section("6. Redact PII - Text Mode")
    
    payload = {
        "text": "My name is Bob Smith, email bob@company.com, card 5105-1051-0510-5100"
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/api/v1/redact", json=payload, timeout=10)
        result = response.json()
        print_result("POST /api/v1/redact", response.status_code, result)
        
        # Check if redaction happened
        if response.status_code == 200:
            redacted_text = result.get("text", "")
            if "[REDACTED]" in redacted_text:
                print("✓ Redaction with [REDACTED] confirmed")
                return True
            else:
                print("⚠️ Warning: No [REDACTED] found in redacted text")
                return False
        return False
    except Exception as e:
        print_result("POST /api/v1/redact", 0, None, str(e))
        return False


def test_rapidapi_redact_text():
    """Test RapidAPI facade endpoint with text."""
    print_section("7. RapidAPI Facade - Text with Placeholder Mode")
    
    payload = {
        "text": "My name is Charlie Brown, email charlie@peanuts.com",
        "mode": "placeholder",
        "language": "en"
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/v1/redact", json=payload, timeout=10)
        result = response.json()
        print_result("POST /v1/redact (placeholder)", response.status_code, result)
        
        if response.status_code == 200:
            redacted = result.get("redacted_text", "")
            if "<PERSON>" in redacted and "<EMAIL>" in redacted:
                print("✓ Placeholder mode working correctly")
                return True
            else:
                print("⚠️ Warning: Expected placeholders not found")
                return False
        return False
    except Exception as e:
        print_result("POST /v1/redact", 0, None, str(e))
        return False


def test_rapidapi_redact_json():
    """Test RapidAPI facade endpoint with JSON."""
    print_section("8. RapidAPI Facade - JSON with Mask Mode")
    
    payload = {
        "json": {
            "user": "David Lee",
            "contact": "david@demo.com"
        },
        "mode": "mask"
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/v1/redact", json=payload, timeout=10)
        print_result("POST /v1/redact (JSON mask)", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print_result("POST /v1/redact (JSON)", 0, None, str(e))
        return False


def test_entity_filtering():
    """Test entity type filtering."""
    print_section("9. Entity Filtering - Only EMAIL")
    
    payload = {
        "text": "Contact John at john@example.com or call +1-555-1234",
        "entities": ["EMAIL"]
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/api/v1/detect", json=payload, timeout=10)
        result = response.json()
        print_result("POST /api/v1/detect (filter EMAIL)", response.status_code, result)
        
        if response.status_code == 200:
            entities = result.get("entities", [])
            if entities and all(e.get("type") == "EMAIL" for e in entities):
                print("✓ Entity filtering working correctly (only EMAIL detected)")
                return True
            elif not entities:
                print("⚠️ Warning: No entities detected")
                return False
        return False
    except Exception as e:
        print_result("POST /api/v1/detect", 0, None, str(e))
        return False


def test_error_cases():
    """Test error handling."""
    print_section("10. Error Handling")
    
    test_cases = [
        {
            "name": "Empty text",
            "payload": {"text": ""},
            "expected_status": 400
        },
        {
            "name": "No text or json",
            "payload": {},
            "expected_status": 400
        },
        {
            "name": "Both text and json",
            "payload": {"text": "test", "json": {}},
            "expected_status": 400
        },
        {
            "name": "Invalid language",
            "payload": {"text": "test", "language": "invalid"},
            "expected_status": 400
        },
    ]
    
    success_count = 0
    for case in test_cases:
        print(f"\nTest: {case['name']}")
        try:
            response = httpx.post(f"{BASE_URL}/api/v1/detect", json=case["payload"], timeout=10)
            if response.status_code == case["expected_status"]:
                print(f"✅ Correct error status {response.status_code}")
                success_count += 1
            else:
                print(f"⚠️ Expected {case['expected_status']}, got {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return success_count == len(test_cases)


def test_docs():
    """Test API documentation endpoints."""
    print_section("11. API Documentation")
    
    endpoints = [
        ("GET /docs", f"{BASE_URL}/docs"),
        ("GET /redoc", f"{BASE_URL}/redoc"),
        ("GET /openapi.json", f"{BASE_URL}/openapi.json"),
    ]
    
    success_count = 0
    for name, url in endpoints:
        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
            if response.status_code == 200:
                print(f"✅ {name} - OK")
                success_count += 1
            else:
                print(f"⚠️ {name} - status {response.status_code}")
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
    
    return success_count == len(endpoints)


def main():
    """Run all tests."""
    print_section("🚀 MASKER API MANUAL TESTING")
    print("Testing all endpoints as a real user...")
    
    results = {
        "Health Check": test_health(),
        "Detect Text": test_detect_text(),
        "Detect JSON": test_detect_json(),
        "Mask Text": test_mask_text(),
        "Mask JSON": test_mask_json(),
        "Redact Text": test_redact_text(),
        "RapidAPI Text": test_rapidapi_redact_text(),
        "RapidAPI JSON": test_rapidapi_redact_json(),
        "Entity Filtering": test_entity_filtering(),
        "Error Handling": test_error_cases(),
        "Documentation": test_docs(),
    }
    
    print_section("📊 FINAL RESULTS")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'=' * 80}")
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print('=' * 80)
    
    if passed == total:
        print("\n🎉 All tests passed! API is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Issues need to be fixed.")
        return 1


if __name__ == "__main__":
    exit(main())
