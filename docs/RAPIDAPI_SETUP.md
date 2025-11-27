# RapidAPI Listing Setup Guide

**API Name:** Masker - PII Redaction API  
**Base URL:** `https://masker.kikuai.dev`  
**Primary Endpoint:** `POST /v1/redact`

---

## 📋 Информация для RapidAPI Provider Dashboard

### Basic Information

**API Name:**
```
Masker - PII Redaction API
```

**Short Description:**
```
Remove personal information from text and JSON before sending to LLMs like ChatGPT, Claude, etc.
```

**Full Description:**
```
Masker is a privacy-first API that detects and redacts personally identifiable information (PII) from text and JSON data. Perfect for cleaning user input before sending to AI models, anonymizing support tickets, processing form data, and sanitizing logs.

**Key Features:**
- Text & JSON processing modes
- Multiple redaction styles (mask, placeholder)
- Detects: EMAIL, PHONE, CARD, PERSON (names)
- Multi-language support (English, Russian)
- Stateless & privacy-first (no data storage)
- Fast processing (~15-25ms average)

**Use Cases:**
- Clean user messages before ChatGPT/Claude
- Anonymize support tickets for AI analysis
- Process form data before LLM classification
- Sanitize logs for AI-powered monitoring
```

**Category:**
```
Text Analysis / Data Privacy / AI/ML
```

**Tags:**
```
pii, redaction, privacy, anonymization, data-cleaning, llm, chatgpt, claude, nlp, text-processing
```

---

## 🔗 Endpoints Configuration

### Primary Endpoint

**Endpoint Name:** `Redact PII`

**Method:** `POST`

**Path:** `/v1/redact`

**Description:**
```
Unified endpoint for PII redaction. Supports both text and JSON input modes with flexible redaction styles.
```

**Request Headers:**
```
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "text": "string (optional, one of text/json required)",
  "json": "object (optional, one of text/json required)",
  "mode": "string (optional, default: 'mask', values: 'mask' | 'placeholder')",
  "entities": "array (optional, values: 'PERSON' | 'EMAIL' | 'PHONE' | 'CARD')",
  "language": "string (optional, default: 'en', values: 'en' | 'ru')"
}
```

**Request Example:**
```json
{
  "text": "Contact John Doe at john@example.com or call 555-123-4567",
  "mode": "placeholder"
}
```

**Response Schema:**
```json
{
  "redacted_text": "string | null",
  "redacted_json": "object | null",
  "items": [
    {
      "entity_type": "string",
      "path": "string | null",
      "start": "number",
      "end": "number",
      "score": "number"
    }
  ],
  "processing_time_ms": "number"
}
```

**Response Example:**
```json
{
  "redacted_text": "Contact <PERSON> at <EMAIL> or call <PHONE>",
  "redacted_json": null,
  "items": [
    {
      "entity_type": "PERSON",
      "path": null,
      "start": 8,
      "end": 16,
      "score": 0.85
    },
    {
      "entity_type": "EMAIL",
      "path": null,
      "start": 20,
      "end": 36,
      "score": 1.0
    },
    {
      "entity_type": "PHONE",
      "path": null,
      "start": 45,
      "end": 57,
      "score": 1.0
    }
  ],
  "processing_time_ms": 15.29
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input or validation error
- `413 Payload Too Large` - Request body exceeds 64KB limit
- `500 Internal Server Error` - Server error

---

## 💰 Pricing Tiers

### Free Tier
- **Price:** $0
- **Requests:** 100 per day
- **Rate Limit:** 10 requests per minute
- **Description:** Perfect for testing and small projects

### Basic Tier
- **Price:** $9/month
- **Requests:** 10,000 per month
- **Rate Limit:** 100 requests per minute
- **Description:** Ideal for small to medium applications

### Pro Tier
- **Price:** $29/month
- **Requests:** 100,000 per month
- **Rate Limit:** 500 requests per minute
- **Description:** For high-volume applications and production use

### Enterprise Tier
- **Price:** Custom
- **Requests:** Unlimited
- **Rate Limit:** Custom
- **Description:** Custom pricing and SLA for enterprise customers

---

## 📝 Code Examples

### Python
```python
import requests

url = "https://masker.kikuai.dev/v1/redact"
headers = {
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
    "Content-Type": "application/json"
}

data = {
    "text": "Contact John Doe at john@example.com",
    "mode": "placeholder"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(result["redacted_text"])
# Output: "Contact <PERSON> at <EMAIL>"
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

const url = 'https://masker.kikuai.dev/v1/redact';
const headers = {
  'X-RapidAPI-Key': 'YOUR_RAPIDAPI_KEY',
  'Content-Type': 'application/json'
};

const data = {
  text: 'Contact John Doe at john@example.com',
  mode: 'placeholder'
};

axios.post(url, data, { headers })
  .then(response => {
    console.log(response.data.redacted_text);
    // Output: "Contact <PERSON> at <EMAIL>"
  })
  .catch(error => {
    console.error('Error:', error.response.data);
  });
```

### cURL
```bash
curl -X POST "https://masker.kikuai.dev/v1/redact" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact John Doe at john@example.com",
    "mode": "placeholder"
  }'
```

### JSON Mode Example
```python
import requests

url = "https://masker.kikuai.dev/v1/redact"
headers = {
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
    "Content-Type": "application/json"
}

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

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(result["redacted_json"])
# Output: {
#   "user": {
#     "name": "<PERSON>",
#     "email": "<EMAIL>",
#     "phone": "<PHONE>"
#   }
# }
```

---

## 🔒 Authentication

RapidAPI handles authentication automatically via the `X-RapidAPI-Key` header. No additional authentication setup is required.

---

## 📊 Rate Limits

Rate limits are enforced by RapidAPI based on the selected pricing tier:
- **Free:** 10 requests/minute
- **Basic:** 100 requests/minute
- **Pro:** 500 requests/minute
- **Enterprise:** Custom

---

## ⚠️ Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request body format and required fields |
| 413 | Payload Too Large | Reduce request size (max 64KB) |
| 429 | Too Many Requests | Wait before making more requests |
| 500 | Internal Server Error | Contact support if issue persists |

---

## 📚 Additional Resources

- **API Documentation:** https://masker.kikuai.dev/docs
- **OpenAPI Spec:** https://masker.kikuai.dev/openapi.json
- **Health Check:** https://masker.kikuai.dev/health
- **GitHub:** https://github.com/KikuAI-Lab/masker

---

## 🚀 Quick Start

1. **Get API Key:** Subscribe to a pricing tier on RapidAPI
2. **Make Request:** Use the `/v1/redact` endpoint with your API key
3. **Process Response:** Extract `redacted_text` or `redacted_json` from response
4. **Send to LLM:** Use the cleaned data with ChatGPT, Claude, etc.

---

**Last Updated:** 2025-11-27  
**API Version:** 1.0.0

