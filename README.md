# Masker - PII Redaction & Text Anonymization API for LLMs and JSON

A lightweight, stateless HTTP API for detecting and masking personally identifiable information (PII) in text and JSON — **optimized for cleaning data before sending to LLMs like ChatGPT, Claude, and others.**

## Why Masker?

When building LLM-powered applications, you often need to:
- Remove personal data before sending prompts to AI models
- Anonymize JSON payloads from your backend
- Comply with privacy regulations while using third-party AI services

Masker provides a simple HTTP API that does exactly this — no complex setup, no data storage, just clean redaction.

## Features

- **Text mode**: Process plain text strings
- **JSON mode**: Process JSON objects/arrays recursively (only string values are modified)
- **Multiple modes**: Mask (`***`), redact (`[REDACTED]`), or use placeholders (`<PERSON>`)
- **Entity filtering**: Choose which PII types to redact
- **Stateless & private**: No data stored, no content logged

### Supported PII Types

| Type | Description | Detection Method |
|------|-------------|------------------|
| EMAIL | Email addresses | Regex |
| PHONE | International phone numbers | Regex |
| CARD | Credit/debit card numbers | Regex |
| PERSON | Person names | NER (spaCy EN+RU) |

### Supported Languages

- English (`en`) - default
- Russian (`ru`)

---

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download ru_core_news_sm

# Run the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Docker

```bash
docker build -t masker-api .
docker run -p 8000:8000 masker-api
```

---

## Use with LLMs

### Python Example: Redact Before Calling OpenAI

```python
import httpx
from openai import OpenAI

MASKER_URL = "http://localhost:8000/v1/redact"

def redact_pii(text: str) -> str:
    """Remove PII from text before sending to LLM."""
    response = httpx.post(
        MASKER_URL,
        json={"text": text, "mode": "placeholder"}
    )
    return response.json()["redacted_text"]

# Usage
client = OpenAI()
user_message = "My name is John Doe and my email is john@example.com"

# Clean the message first
safe_message = redact_pii(user_message)
# safe_message = "My name is <PERSON> and my email is <EMAIL>"

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": safe_message}]
)
```

### Python Example: Redact JSON Payloads

```python
import httpx

MASKER_URL = "http://localhost:8000/v1/redact"

def redact_json(data: dict) -> dict:
    """Remove PII from JSON before processing."""
    response = httpx.post(
        MASKER_URL,
        json={"json": data, "mode": "mask"}
    )
    return response.json()["redacted_json"]

# Usage
user_data = {
    "user": {
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {"theme": "dark"}
    },
    "message": "Call me at +1-555-123-4567"
}

safe_data = redact_json(user_data)
# Result:
# {
#     "user": {
#         "name": "***",
#         "email": "***",
#         "preferences": {"theme": "dark"}  # Non-PII preserved
#     },
#     "message": "Call me at ***"
# }
```

### Middleware Pattern

```python
from functools import wraps
import httpx

def with_pii_redaction(func):
    """Decorator to redact PII from function arguments."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Redact text arguments
        if 'text' in kwargs:
            response = httpx.post(
                "http://localhost:8000/v1/redact",
                json={"text": kwargs['text'], "mode": "placeholder"}
            )
            kwargs['text'] = response.json()["redacted_text"]
        return func(*args, **kwargs)
    return wrapper

@with_pii_redaction
def send_to_llm(text: str):
    # Text is already redacted when this runs
    pass
```

---

## API Endpoints

### Health Check

```bash
GET /health
```

### Text Mode Examples

**Detect PII:**
```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact john@example.com"}'
```

**Mask PII (replace with `***`):**
```bash
curl -X POST "http://localhost:8000/api/v1/mask" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact john@example.com"}'
# {"text": "Contact ***", "entities": [...]}
```

**Redact PII (replace with `[REDACTED]`):**
```bash
curl -X POST "http://localhost:8000/api/v1/redact" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact john@example.com"}'
# {"text": "Contact [REDACTED]", "entities": [...]}
```

### JSON Mode Examples

**Mask PII in JSON:**
```bash
curl -X POST "http://localhost:8000/api/v1/mask" \
  -H "Content-Type: application/json" \
  -d '{
    "json": {
      "user": {"name": "John Doe", "email": "john@example.com"},
      "count": 42
    }
  }'
```

Response:
```json
{
  "json": {
    "user": {"name": "***", "email": "***"},
    "count": 42
  },
  "entities": [
    {"path": "user.name", "type": "PERSON", "value": "John Doe", "start": 0, "end": 8},
    {"path": "user.email", "type": "EMAIL", "value": "john@example.com", "start": 0, "end": 16}
  ]
}
```

---

## Public Endpoint for RapidAPI: POST /v1/redact

Unified endpoint designed for RapidAPI integration — **redact PII before sending to LLM**.

```bash
POST /v1/redact
Content-Type: application/json

{
  "text": "Hello, my name is John Doe and my email is john@example.com",
  "language": "en",
  "entities": ["PERSON", "EMAIL"],
  "mode": "placeholder"
}
```

Or with JSON input:

```bash
POST /v1/redact
Content-Type: application/json

{
  "json": {"user": {"name": "John Doe", "email": "john@example.com"}},
  "mode": "mask"
}
```

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| text | string | One of text/json | - | Text to process (max 32KB) |
| json | object | One of text/json | - | JSON to process recursively |
| language | string | No | "en" | Language code: "en" or "ru" |
| entities | array | No | null | Entity types to redact: `["PERSON", "EMAIL", "PHONE", "CARD"]` |
| mode | string | No | "mask" | `"mask"` (***) or `"placeholder"` (<TYPE>) |

### Response (Text Mode)

```json
{
  "redacted_text": "Hello, my name is <PERSON> and my email is <EMAIL>",
  "redacted_json": null,
  "items": [
    {"entity_type": "PERSON", "start": 18, "end": 26, "score": 0.85},
    {"entity_type": "EMAIL", "start": 43, "end": 59, "score": 1.0}
  ],
  "processing_time_ms": 45.2
}
```

### Response (JSON Mode)

```json
{
  "redacted_text": null,
  "redacted_json": {"user": {"name": "***", "email": "***"}},
  "items": [
    {"entity_type": "PERSON", "path": "user.name", "start": 0, "end": 8, "score": 0.85}
  ],
  "processing_time_ms": 32.1
}
```

---

## Privacy & Data Handling

Masker is designed with privacy as a core principle:

### What We Process
- Text strings and JSON payloads sent via HTTP POST
- Only string values in JSON are scanned for PII

### What We Do NOT Store
- **No database**: All processing is in-memory, stateless
- **No file storage**: Nothing is written to disk
- **No content logging**: Request/response bodies are never logged

### What We Log (Service Metadata Only)
```
2024-01-15 10:30:45 - masker - INFO - request: method=POST path=/v1/redact status=200 content_length=128 duration_ms=45.20
```

Only: HTTP method, path, status code, payload size, processing time.

### Security Features
- Stateless processing
- Non-root Docker user
- Configurable size limits (default: 32KB text, 64KB payload)

---

## Configuration

Environment variables (prefix `MASKER_`):

| Variable | Default | Description |
|----------|---------|-------------|
| MASKER_MAX_TEXT_SIZE | 32768 | Maximum text size in bytes |
| MASKER_MAX_PAYLOAD_SIZE | 65536 | Maximum JSON payload size in bytes |
| MASKER_MASK_TOKEN | *** | Replacement for mask mode |
| MASKER_REDACT_TOKEN | [REDACTED] | Replacement for redact mode |

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Invalid request (missing/empty text, invalid language, both text and json provided) |
| 413 | Payload too large |
| 500 | Internal server error |

---

## OpenAPI Documentation

When the server is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/detect` | POST | Detect PII (text or JSON) |
| `/api/v1/mask` | POST | Mask PII with *** (text or JSON) |
| `/api/v1/redact` | POST | Redact PII with [REDACTED] (text or JSON) |
| `/v1/redact` | POST | RapidAPI facade (text or JSON, configurable mode) |

---

## License

MIT
