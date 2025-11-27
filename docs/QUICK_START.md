# Masker API - Quick Start Guide

Get started with Masker API in 5 minutes.

---

## 🚀 Step 1: Get Your API Key

1. Go to [RapidAPI Masker Page](https://rapidapi.com/your-username/api/masker)
2. Click "Subscribe" to choose a pricing tier
3. Copy your `X-RapidAPI-Key` from the code examples

---

## 📝 Step 2: Make Your First Request

### Example: Redact PII from Text

**Request:**
```bash
curl -X POST "https://masker.kikuai.dev/v1/redact" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact John Doe at john@example.com or call 555-123-4567",
    "mode": "placeholder"
  }'
```

**Response:**
```json
{
  "redacted_text": "Contact <PERSON> at <EMAIL> or call <PHONE>",
  "redacted_json": null,
  "items": [
    {
      "entity_type": "PERSON",
      "start": 8,
      "end": 16,
      "score": 0.85
    },
    {
      "entity_type": "EMAIL",
      "start": 20,
      "end": 36,
      "score": 1.0
    },
    {
      "entity_type": "PHONE",
      "start": 45,
      "end": 57,
      "score": 1.0
    }
  ],
  "processing_time_ms": 15.29
}
```

---

## 🎯 Step 3: Use Cases

### Use Case 1: Clean User Input Before ChatGPT

```python
import requests
from openai import OpenAI

# Step 1: Redact PII
masker_url = "https://masker.kikuai.dev/v1/redact"
response = requests.post(
    masker_url,
    json={"text": user_message, "mode": "placeholder"},
    headers={"X-RapidAPI-Key": "YOUR_KEY"}
)
safe_message = response.json()["redacted_text"]

# Step 2: Send to ChatGPT
client = OpenAI()
chat_response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": safe_message}]
)
```

### Use Case 2: Process JSON Data

```python
import requests

data = {
    "json": {
        "user": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-123-4567"
        }
    },
    "mode": "placeholder"
}

response = requests.post(
    "https://masker.kikuai.dev/v1/redact",
    json=data,
    headers={"X-RapidAPI-Key": "YOUR_KEY"}
)

cleaned_data = response.json()["redacted_json"]
# Result: {"user": {"name": "<PERSON>", "email": "<EMAIL>", "phone": "<PHONE>"}}
```

---

## 🔧 Redaction Modes

### Mode: `mask` (default)
Replaces PII with `***`

```json
{
  "text": "Contact john@example.com",
  "mode": "mask"
}
```

**Result:** `"Contact ***"`

### Mode: `placeholder`
Replaces PII with type placeholders like `<EMAIL>`, `<PERSON>`, etc.

```json
{
  "text": "Contact john@example.com",
  "mode": "placeholder"
}
```

**Result:** `"Contact <EMAIL>"`

---

## 🎛️ Entity Filtering

Only redact specific PII types:

```json
{
  "text": "John Doe's email is john@example.com and phone is 555-123-4567",
  "mode": "placeholder",
  "entities": ["EMAIL", "PHONE"]
}
```

**Result:** `"<PERSON>'s email is <EMAIL> and phone is <PHONE>"`

Note: `PERSON` is not redacted because it's not in the `entities` filter.

---

## 📊 Supported PII Types

| Type | Description | Example |
|------|-------------|---------|
| **EMAIL** | Email addresses | `john@example.com` |
| **PHONE** | Phone numbers | `+1-555-123-4567` |
| **CARD** | Credit card numbers | `4111-1111-1111-1111` |
| **PERSON** | Person names | `John Doe` |

---

## 🌍 Language Support

Default language is English. For Russian text:

```json
{
  "text": "Иван Иванов, email: ivan@example.com",
  "language": "ru"
}
```

---

## ⚡ Response Time

Average processing time: **15-25ms**

Check `processing_time_ms` in the response for actual time.

---

## ❓ Common Questions

**Q: What's the maximum request size?**  
A: 64KB for the entire JSON payload, 32KB for text field.

**Q: Is my data stored?**  
A: No. Masker is completely stateless - no data is stored or logged.

**Q: Can I use this for production?**  
A: Yes! The API is production-ready with 99.9% uptime SLA on Pro tier.

**Q: What happens if I exceed rate limits?**  
A: You'll receive a 429 Too Many Requests error. Wait a minute and try again.

---

## 🆘 Need Help?

- **Documentation:** https://masker.kikuai.dev/docs
- **Support:** Contact through RapidAPI
- **GitHub:** https://github.com/KikuAI-Lab/masker

---

**Ready to start?** Subscribe on RapidAPI and make your first request! 🚀

