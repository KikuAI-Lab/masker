"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.
    
    All settings can be overridden via environment variables.
    """
    
    model_config = SettingsConfigDict(env_prefix="MASKER_")
    
    # API settings
    api_title: str = "Masker API - PII Redaction for LLMs"
    api_description: str = """
# 🔒 Masker API - Privacy-First PII Redaction

**Remove personal information from text and JSON before sending to ChatGPT, Claude, or any LLM.**

## 🎯 What is Masker?

Masker is a **stateless, privacy-first API** that detects and redacts personally identifiable information (PII) from your data. Perfect for cleaning user input before sending to AI models.

## 🔐 Privacy Guarantee

**We store NOTHING. We log NOTHING. Your data is processed in-memory and immediately discarded.**

- ✅ No database - All processing is in-memory
- ✅ No file storage - Nothing is written to disk  
- ✅ No content logging - Only metadata is logged
- ✅ Stateless - Each request is independent
- ✅ GDPR compliant - No personal data retention

## 🚀 Quick Start

### Text Mode Example
```bash
curl -X POST "https://masker.kikuai.dev/v1/redact" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Contact John Doe at john@example.com",
    "mode": "placeholder"
  }'
```

### JSON Mode Example
```bash
curl -X POST "https://masker.kikuai.dev/v1/redact" \\
  -H "Content-Type: application/json" \\
  -d '{
    "json": {
      "user": {
        "name": "John Doe",
        "email": "john@example.com"
      }
    },
    "mode": "placeholder"
  }'
```

## 📚 Endpoints Overview

### Main Endpoint
- **POST `/v1/redact`** - Main endpoint for PII redaction (supports text & JSON, flexible modes)

### Standard Endpoints
- **POST `/api/v1/detect`** - Detect PII without modifying content
- **POST `/api/v1/mask`** - Mask PII with `***`
- **POST `/api/v1/redact`** - Redact PII with `[REDACTED]`

### Utility Endpoints
- **GET `/health`** - Health check endpoint
- **GET `/docs`** - This interactive documentation

## 🎯 Supported PII Types

| Type | Detection Method | Accuracy |
|------|----------------|----------|
| **EMAIL** | Regex | 100% |
| **PHONE** | Regex (international) | 100% |
| **CARD** | Regex + Luhn validation | 100% |
| **PERSON** | spaCy NER (EN/RU) | ~85% |

## 🔧 Redaction Modes

- **`mask`** - Replace PII with `***`
- **`placeholder`** - Replace PII with type placeholders like `<PERSON>`, `<EMAIL>`, etc.

## 📖 Full Documentation

- [Wiki Documentation](https://github.com/KikuAI-Lab/masker/wiki)
- [Landing Page](https://kikuai-lab.github.io/masker/)

## 🔒 Privacy & Security

All requests are processed in-memory. No data is stored, logged, or retained. See [Privacy Policy](https://github.com/KikuAI-Lab/masker/wiki/Privacy-Policy) for details.
"""
    api_version: str = "1.0.0"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Request limits
    max_text_size: int = 32 * 1024  # 32KB for text field
    max_payload_size: int = 64 * 1024  # 64KB for entire JSON payload
    
    # Supported languages for NER
    supported_languages: list[str] = ["en", "ru"]
    default_language: str = "en"
    
    # Masking/redaction tokens (configurable defaults)
    mask_token: str = "***"
    redact_token: str = "[REDACTED]"
    
    # Placeholder templates for typed redaction
    placeholder_person: str = "<PERSON>"
    placeholder_email: str = "<EMAIL>"
    placeholder_phone: str = "<PHONE>"
    placeholder_card: str = "<CARD>"


# Global settings instance
settings = Settings()
