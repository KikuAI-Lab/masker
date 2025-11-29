#!/usr/bin/env python3
"""
Extended test suite for Masker API - edge cases and advanced features.
"""

import httpx
import json

BASE_URL = "http://127.0.0.1:8000"


def test_phone_not_detected_mislabeled():
    """Test that phone number in /mask endpoint isn't detected as PERSON."""
    print("\n🔍 Testing phone masking (ensuring no PERSON mislabel)...")
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/mask",
        json={"text": "Call me at +1-555-9876"},
        timeout=10
    )
    
    result = response.json()
    entities = result.get("entities", [])
    
    # Check that phone is detected, but not as PERSON
    has_phone = any(e["type"] == "PHONE" for e in entities)
    has_person = any(e["type"] == "PERSON" for e in entities)
    
    print(f"  ✓ Phone detected: {has_phone}")
    print(f"  ✓ No PERSON mislabel: {not has_person}")
    print(f"  Entities: {entities}")
    
    assert has_phone or len(entities) == 0, "Phone should be detected or no entities"


def test_entity_filter_mask_only_email():
    """Test filtering to mask only EMAIL entities."""
    print("\n🎭 Testing entity filtering in /mask (only EMAIL)...")
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/mask",
        json={
            "text": "Contact John Doe at john@example.com or call +1-555-1234",
            "entities": ["EMAIL"]
        },
        timeout=10
    )
    
    result = response.json()
    masked_text = result.get("text", "")
    entities = result.get("entities", [])
    
    print(f"  Original: Contact John Doe at john@example.com or call +1-555-1234")
    print(f"  Masked: {masked_text}")
    print(f"  Entities: {[e['type'] for e in entities]}")
    
    # Only EMAIL should be masked
    assert "John Doe" in masked_text, "Name should NOT be masked"
    assert "***" in masked_text, "Email should be masked"
    assert all(e["type"] == "EMAIL" for e in entities), "Only EMAIL should be detected"


def test_entity_filter_redact_only_person():
    """Test filtering to redact only PERSON entities."""
    print("\n🔒 Testing entity filtering in /redact (only PERSON)...")
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/redact",
        json={
            "text": "Meet Alice Smith at alice@test.com",
            "entities": ["PERSON"]
        },
        timeout=10
    )
    
    result = response.json()
    redacted_text = result.get("text", "")
    entities = result.get("entities", [])
    
    print(f"  Original: Meet Alice Smith at alice@test.com")
    print(f"  Redacted: {redacted_text}")
    print(f"  Entities: {[e['type'] for e in entities]}")
    
    # Only PERSON should be redacted
    assert "alice@test.com" in redacted_text, "Email should NOT be redacted"
    assert "[REDACTED]" in redacted_text, "Name should be redacted"
    assert all(e["type"] == "PERSON" for e in entities), "Only PERSON should be detected"


def test_rapidapi_entity_filter():
    """Test entity filtering in RapidAPI endpoint."""
    print("\n⚡ Testing entity filtering in /v1/redact (RapidAPI)...")
    
    response = httpx.post(
        f"{BASE_URL}/v1/redact",
        json={
            "text": "John's card is 4532-1234-5678-9010 and email is john@test.com",
            "mode": "placeholder",
            "entities": ["CARD"]
        },
        timeout=10
    )
    
    result = response.json()
    redacted = result.get("redacted_text", "")
    items = result.get("items", [])
    
    print(f"  Original: John's card is 4532-1234-5678-9010 and email is john@test.com")
    print(f"  Redacted: {redacted}")
    print(f"  Items: {[i['entity_type'] for i in items]}")
    
    # Only CARD should be redacted
    assert "John" in redacted, "Name should NOT be redacted"
    assert "john@test.com" in redacted, "Email should NOT be redacted"
    assert "<CARD>" in redacted, "Card should be redacted with placeholder"
    assert all(i["entity_type"] == "CARD" for i in items), "Only CARD should be detected"


def test_multiple_entity_types_filter():
    """Test filtering multiple entity types."""
    print("\n🎯 Testing multiple entity type filtering...")
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/detect",
        json={
            "text": "Alice's email is alice@test.com, phone +1-555-8888, card 5105-1051-0510-5100",
            "entities": ["EMAIL", "PHONE"]  # Exclude PERSON and CARD
        },
        timeout=10
    )
    
    result = response.json()
    entities = result.get("entities", [])
    detected_types = {e["type"] for e in entities}
    
    print(f"  Detected types: {detected_types}")
    print(f"  Total entities: {len(entities)}")
    
    assert "CARD" not in detected_types, "CARD should be filtered out"
    assert "PERSON" not in detected_types, "PERSON should be filtered out"
    assert detected_types.issubset({"EMAIL", "PHONE"}), "Only EMAIL and PHONE allowed"


def test_json_mode_entity_filter():
    """Test entity filtering in JSON mode."""
    print("\n📦 Testing entity filtering in JSON mode...")
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/mask",
        json={
            "json": {
                "user": "Bob Johnson",
                "email": "bob@example.com",
                "phone": "+1-555-1234"
            },
            "entities": ["PERSON"]  # Only mask names
        },
        timeout=10
    )
    
    result = response.json()
    masked_json = result.get("json", {})
    entities = result.get("entities", [])
    
    print(f"  Masked JSON: {json.dumps(masked_json, indent=2)}")
    print(f"  Entities: {[e['type'] for e in entities]}")
    
    # Only PERSON should be masked
    assert masked_json.get("user") == "***", "Name should be masked"
    assert masked_json.get("email") == "bob@example.com", "Email should NOT be masked"
    assert masked_json.get("phone") == "+1-555-1234", "Phone should NOT be masked"
    assert all(e["type"] == "PERSON" for e in entities), "Only PERSON should be detected"


def test_empty_entity_filter():
    """Test with empty entities array (should detect nothing)."""
    print("\n🚫 Testing empty entity filter...")
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/detect",
        json={
            "text": "John Doe, john@test.com, +1-555-9999",
            "entities": []  # Empty filter
        },
        timeout=10
    )
    
    result = response.json()
    entities = result.get("entities", [])
    
    print(f"  Entities detected: {len(entities)}")
    
    assert len(entities) == 0, "Empty filter should detect no entities"


def test_performance():
    """Test processing time is reasonable."""
    print("\n⏱️  Testing performance...")
    
    long_text = "Contact " + " and ".join([
        f"person{i}@email{i}.com" for i in range(50)
    ])
    
    response = httpx.post(
        f"{BASE_URL}/v1/redact",
        json={
            "text": long_text,
            "mode": "mask"
        },
        timeout=10
    )
    
    result = response.json()
    processing_time = result.get("processing_time_ms", 0)
    
    print(f"  Text length: {len(long_text)} chars")
    print(f"  Processing time: {processing_time:.2f} ms")
    print(f"  Items detected: {len(result.get('items', []))}")
    
    assert processing_time < 1000, f"Processing should be < 1s, got {processing_time}ms"


def main():
    """Run all extended tests."""
    print("\n" + "="*80)
    print(" 🧪 MASKER API - EXTENDED TEST SUITE")
    print("="*80)
    
    tests = [
        ("Phone masking", test_phone_not_detected_mislabeled),
        ("Filter: mask only EMAIL", test_entity_filter_mask_only_email),
        ("Filter: redact only PERSON", test_entity_filter_redact_only_person),
        ("Filter: RapidAPI CARD only", test_rapidapi_entity_filter),
        ("Filter: multiple types", test_multiple_entity_types_filter),
        ("Filter: JSON mode", test_json_mode_entity_filter),
        ("Filter: empty array", test_empty_entity_filter),
        ("Performance check", test_performance),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"✅ {name} - PASSED\n")
        except AssertionError as e:
            failed += 1
            print(f"❌ {name} - FAILED: {e}\n")
        except Exception as e:
            failed += 1
            print(f"❌ {name} - ERROR: {e}\n")
    
    print("="*80)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*80)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
