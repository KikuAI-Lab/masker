"""
Masker API - Python Example

This example shows how to use Masker API to clean PII before sending to ChatGPT.
"""

import requests
from typing import Dict, Any

# API endpoint
MASKER_API_URL = "https://masker.kikuai.dev/v1/redact"


def redact_pii(text: str, mode: str = "placeholder") -> str:
    """
    Redact PII from text using Masker API.
    
    Args:
        text: Text containing PII
        mode: Redaction mode - "mask" or "placeholder"
    
    Returns:
        Text with PII redacted
    """
    response = requests.post(
        MASKER_API_URL,
        json={"text": text, "mode": mode},
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()["redacted_text"]


def redact_json(data: Dict[str, Any], mode: str = "placeholder") -> Dict[str, Any]:
    """
    Redact PII from JSON structure using Masker API.
    
    Args:
        data: JSON object containing PII
        mode: Redaction mode - "mask" or "placeholder"
    
    Returns:
        JSON object with PII redacted
    """
    response = requests.post(
        MASKER_API_URL,
        json={"json": data, "mode": mode},
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()["redacted_json"]


# Example 1: Clean user message before ChatGPT
def example_chatgpt_cleanup():
    """Example: Clean user input before sending to ChatGPT."""
    user_message = "My name is John Doe and my email is john@example.com"
    
    # Clean the message
    safe_message = redact_pii(user_message, mode="placeholder")
    print(f"Original: {user_message}")
    print(f"Cleaned:  {safe_message}")
    # Output: "My name is <PERSON> and my email is <EMAIL>"
    
    # Now safe to send to ChatGPT
    # chatgpt_response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": safe_message}]
    # )


# Example 2: Anonymize support ticket
def example_support_ticket():
    """Example: Anonymize support ticket for AI analysis."""
    ticket = {
        "customer": "John Doe",
        "email": "john@example.com",
        "phone": "555-123-4567",
        "issue": "Can't login to my account"
    }
    
    # Anonymize
    anonymized = redact_json(ticket, mode="placeholder")
    print("Original ticket:", ticket)
    print("Anonymized:", anonymized)
    # Output: {"customer": "<PERSON>", "email": "<EMAIL>", "phone": "<PHONE>", "issue": "Can't login to my account"}


# Example 3: Process form data
def example_form_data():
    """Example: Clean form data before LLM classification."""
    form_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "message": "I need help with my order"
    }
    
    # Clean before classification
    cleaned = redact_json(form_data, mode="placeholder")
    print("Original form:", form_data)
    print("Cleaned form:", cleaned)


if __name__ == "__main__":
    print("=== Example 1: ChatGPT Cleanup ===")
    example_chatgpt_cleanup()
    print()
    
    print("=== Example 2: Support Ticket ===")
    example_support_ticket()
    print()
    
    print("=== Example 3: Form Data ===")
    example_form_data()

