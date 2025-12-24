import json

import requests

# Configuration
API_URL = "http://localhost:8000/v1/redact"
# For RapidAPI use: "https://masker-api.p.rapidapi.com/v1/redact"
HEADERS = {
    "Content-Type": "application/json",
    # "X-RapidAPI-Key": "YOUR_KEY"
}

def redact_text():
    """Example of text redaction."""
    payload = {
        "text": "My name is John Doe and my email is john@example.com",
        "mode": "placeholder",
        "entities": ["PERSON", "EMAIL"]
    }

    response = requests.post(API_URL, json=payload, headers=HEADERS)
    print("\n--- Text Redaction ---")
    print(json.dumps(response.json(), indent=2))

def redact_json():
    """Example of JSON redaction."""
    payload = {
        "json": {
            "user": {
                "name": "Alice Smith",
                "contact": {
                    "email": "alice@test.com",
                    "phone": "+1-555-0123"
                }
            },
            "metadata": "User created by admin"
        },
        "mode": "mask"
    }

    response = requests.post(API_URL, json=payload, headers=HEADERS)
    print("\n--- JSON Redaction ---")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    try:
        redact_text()
        redact_json()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the server is running on localhost:8000")
