# Masker - The PII Redaction Firewall

Welcome to Masker. This guide will help you integrate high-performance PII redaction into your applications in minutes.

## 🚀 Quick Start
Masker is designed to be dead simple. You send text, we return purged text.

### Python Example
```python
import requests

url = "https://masker-api.p.rapidapi.com/v1/redact"

payload = {
    "text": "Hello, my name is John Smith and my email is john.smith@example.com",
    "mode": "mask",  # mask (***), placeholder (<EMAIL>), or redact ([REDACTED])
    "language": "en"
}

headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "YOUR_API_KEY",
    "X-RapidAPI-Host": "masker-api.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

**Output:**
```json
{
  "text": "Hello, my name is *** and my email is ***",
  "entities": [
    {
      "type": "PERSON",
      "original": "John Smith",
      "redacted": "***",
      "start": 18,
      "end": 28
    },
    {
      "type": "EMAIL",
      "original": "john.smith@example.com",
      "redacted": "***",
      "start": 45,
      "end": 67
    }
  ],
  "processing_time_ms": 12
}
```

---

## 🛠 Features & Modes

### 1. Redaction Modes
Customize how sensitive data is handled using the `mode` parameter:

| Mode | Description | Example Output | Best For |
|------|-------------|----------------|----------|
| `mask` | Replaces characters with `***` | `Contact *** at ***` | Clean reading, UI display |
| `placeholder` | Replaces with entity type tag | `Contact <PERSON> at <EMAIL>` | LLM training, analytics |
| `redact` | Replaces with `[REDACTED]` | `Contact [REDACTED] at [REDACTED]` | Legal compliance, logs |

### 2. JSON Structure Preserving
Masker isn't just for flat text. You can send complex nested JSON objects, and we'll walk the tree to sanitize every string value.

**Input:**
```json
{
  "user": {
    "name": "Jane Doe",
    "metadata": {
      "ip": "192.168.1.1",
      "note": "Call her at +1-555-0199"
    }
  }
}
```

**Output:**
```json
{
  "user": {
    "name": "***",
    "metadata": {
      "ip": "192.168.1.1",
      "note": "Call her at ***"
    }
  }
}
```
*Note: Keys (`name`, `metadata`) are never touched. Only values are processed.*

### 3. Supported Entities
We automatically detect the following entities:
*   `EMAIL` - Email addresses
*   `PHONE` - International phone numbers
*   `CARD` - Credit cards, debit cards (Luhn validated)
*   `PERSON` - Person names (using Neural NER models)

You can restrict detection to specific types using the `entities` array:
```json
{
  "text": "Call John at 555-0199",
  "entities": ["PHONE"] // Will NOT redact "John"
}
```

---

## ⚡ Performance & Limits
*   **Latency:** P95 < 50ms for typical inputs.
*   **Batch Size:** Ensure payloads are < 5MB.
*   **Concurrency:** Stateless architecture scales horozontally. Contact us for custom enterprise limits.

## 🔒 Security
*   **Stateless:** We do not store your data. Period.
*   **SSL/TLS:** All traffic is encrypted in transit.
*   **No Training:** Your inputs are never used to train our models.

---

## Need Help?
Contact us at [support@kikuai.dev](mailto:support@kikuai.dev) or visit [kikuai.dev](https://kikuai.dev) for more tools.
