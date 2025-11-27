# 🔒 Masker - PII Redaction API for LLMs

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?logo=fastapi)
![spaCy](https://img.shields.io/badge/spaCy-3.7+-orange?logo=spacy)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Privacy-first API that removes personal information from text and JSON before sending to ChatGPT, Claude, or any LLM.**

🔗 **[API Docs](https://masker.kikuai.dev/docs)** | 📖 **[Wiki](https://github.com/KikuAI-Lab/masker/wiki)** | 🌐 **[Landing Page](https://kikuai-lab.github.io/masker/)**

---

## 🎯 What is Masker?

Masker is a **stateless, privacy-first API** that detects and redacts personally identifiable information (PII) from your data. **Perfect for cleaning user input before sending to AI models** like ChatGPT, Claude, Gemini, and others.

### 🔐 Privacy Guarantee

**We store NOTHING. We log NOTHING. Your data is processed in-memory and immediately discarded.**

- ✅ **No database** - All processing is in-memory
- ✅ **No file storage** - Nothing is written to disk
- ✅ **No content logging** - Only metadata (method, path, status) is logged
- ✅ **Stateless** - Each request is independent
- ✅ **GDPR compliant** - No personal data retention

---

## ⚡ Quick Start

### Python Example

```python
import requests

# Redact PII before sending to ChatGPT
response = requests.post(
    "https://masker.kikuai.dev/v1/redact",
    json={
        "text": "My name is John Doe and my email is john@example.com",
        "mode": "placeholder"
    }
)

cleaned_text = response.json()["redacted_text"]
# Result: "My name is <PERSON> and my email is <EMAIL>"

# Now safe to send to ChatGPT
chatgpt_response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": cleaned_text}]
)
```

### cURL Example

```bash
curl -X POST "https://masker.kikuai.dev/v1/redact" \
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
  "items": [
    {"entity_type": "PERSON", "start": 8, "end": 16, "score": 0.85},
    {"entity_type": "EMAIL", "start": 20, "end": 36, "score": 1.0},
    {"entity_type": "PHONE", "start": 45, "end": 57, "score": 1.0}
  ],
  "processing_time_ms": 15.29
}
```

### JSON Mode Example

```python
import requests

# Process entire JSON structures
response = requests.post(
    "https://masker.kikuai.dev/v1/redact",
    json={
        "json": {
            "user": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "555-123-4567"
            }
        },
        "mode": "placeholder"
    }
)

cleaned_data = response.json()["redacted_json"]
# Result: {"user": {"name": "<PERSON>", "email": "<EMAIL>", "phone": "<PHONE>"}}
```

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **🔤 Text Mode** | Process plain text strings |
| **📦 JSON Mode** | Process entire JSON structures recursively (preserves structure) |
| **🎭 Multiple Modes** | `mask` (***), `placeholder` (<TYPE>), `redact` ([REDACTED]) |
| **🎯 Entity Filtering** | Choose which PII types to redact |
| **🌍 Multi-Language** | English & Russian NER support |
| **⚡ Fast** | Average processing time: 15-25ms |
| **🔒 Privacy First** | Stateless, no data storage, no content logging |

### Supported PII Types

| Type | Detection Method | Accuracy |
|------|-----------------|----------|
| **EMAIL** | Regex | 100% |
| **PHONE** | Regex (international) | 100% |
| **CARD** | Regex + Luhn validation | 100% |
| **PERSON** | spaCy NER (EN/RU) | ~85% |

---

---

## 📚 Use Cases

### 1. Clean User Input Before ChatGPT

```python
# User sends message with personal info
user_message = "My name is John and my email is john@example.com"

# Clean it first
cleaned = masker_api.redact(user_message)

# Safe to send to ChatGPT
chatgpt.process(cleaned)  # "My name is <PERSON> and my email is <EMAIL>"
```

### 2. Anonymize Support Tickets

```python
# Support ticket with customer PII
ticket = {
    "customer": "John Doe",
    "email": "john@example.com",
    "issue": "Can't login"
}

# Anonymize for AI analysis
anonymized = masker_api.redact_json(ticket)
# Safe to analyze with AI without exposing customer data
```

### 3. Process Form Data

```python
# Form submission with personal data
form_data = {
    "name": "Jane Smith",
    "phone": "555-123-4567",
    "message": "Need help with my account"
}

# Clean before LLM classification
cleaned = masker_api.redact_json(form_data)
# Classify without exposing PII
```

### 4. Sanitize Logs

```python
# Log entry with sensitive data
log_entry = "User john@example.com accessed resource at 2025-11-27"

# Sanitize for AI-powered monitoring
sanitized = masker_api.redact(log_entry)
# Monitor without exposing user data
```

---

## 🛠️ Technology Stack

### Built With

- **Python 3.11** - Modern Python with type hints
- **FastAPI** - High-performance async web framework
- **spaCy** - Industrial-strength NLP for NER
- **Pydantic** - Data validation with type safety
- **Docker** - Containerized deployment
- **Uvicorn** - ASGI server

### Testing

- **pytest** - Testing framework
- **httpx** - Async HTTP client for tests
- **79 tests** - Comprehensive test coverage

---

## 📖 Documentation

Full documentation available in the **[Wiki](https://github.com/KikuAI-Lab/masker/wiki)**:

- 📘 [Quick Start Guide](https://github.com/KikuAI-Lab/masker/wiki/Quick-Start)
- 📗 [API Reference](https://github.com/KikuAI-Lab/masker/wiki/API-Reference)
- 📙 [Error Codes](https://github.com/KikuAI-Lab/masker/wiki/Error-Codes)
- 📕 [JSON Mode Guide](https://github.com/KikuAI-Lab/masker/wiki/JSON-Mode)
- 📓 [Rate Limits](https://github.com/KikuAI-Lab/masker/wiki/Rate-Limits)
- 🔒 [Privacy Policy](https://github.com/KikuAI-Lab/masker/wiki/Privacy-Policy)

---

## 🔒 Privacy & Security

### What We Process
- Text strings and JSON payloads sent via HTTP POST
- Only string values in JSON are scanned for PII

### What We Do NOT Store
- ❌ **No database** - All processing is in-memory, stateless
- ❌ **No file storage** - Nothing is written to disk
- ❌ **No content logging** - Request/response bodies are never logged

### What We Log (Service Metadata Only)
```
2025-11-27 10:30:45 - masker - INFO - request: method=POST path=/v1/redact status=200 content_length=128 duration_ms=45.20 request_id=abc123
```

**Only:** HTTP method, path, status code, payload size, processing time, request ID.

**Never:** Request body, response body, PII content, user data.

---

## 🧪 Example Code

See the [examples directory](examples/) for complete code samples:

- [Python example](examples/python_example.py)
- [JavaScript example](examples/javascript_example.js)
- [Test examples](tests/)

---

## 🚀 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/redact` | POST | Main endpoint - redact PII in text or JSON |
| `/api/v1/detect` | POST | Detect PII without modifying content |
| `/api/v1/mask` | POST | Mask PII with `***` |
| `/api/v1/redact` | POST | Redact PII with `[REDACTED]` |
| `/health` | GET | Health check endpoint |

**Live API:** https://masker.kikuai.dev  
**Interactive Docs:** https://masker.kikuai.dev/docs

---

## 📊 Performance

- **Average response time:** 15-25ms
- **Health check:** ~170ms
- **Concurrent requests:** Handles high load efficiently

---

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- NLP powered by [spaCy](https://spacy.io/)
- Deployed on [Hetzner Cloud](https://www.hetzner.com/)

---

**Built with ❤️ by [KikuAI Lab](https://kikuai.dev)**

🔒 **Privacy First. No Data Storage. No Logging. Ever.**
