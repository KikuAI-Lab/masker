# Masker Application Code

Core FastAPI application for PII redaction.

## Structure

```
app/
├── main.py           # FastAPI app entry point
├── api/              # API endpoints
│   ├── v1/           # Version 1 endpoints (detect, mask, redact)
│   ├── rapidapi/     # RapidAPI-specific endpoints
│   └── proxy/        # LLM proxy (/v1/chat/completions)
├── core/             # Configuration and logging
├── middleware/       # Auth, rate limiting, metrics
├── models/           # Pydantic schemas
└── services/         # Business logic
    ├── pii_detector.py   # PII detection (regex + spaCy NER)
    ├── api_keys.py       # API key validation
    ├── policy.py         # Redaction policy management
    └── audit.py          # Audit logging
```

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app, middleware, routes |
| `services/pii_detector.py` | EMAIL, PHONE, CARD, PERSON detection |
| `services/policy.py` | YAML policy loading and application |
| `api/proxy/chat.py` | OpenAI-compatible proxy endpoint |
