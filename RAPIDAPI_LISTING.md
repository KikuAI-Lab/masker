# Masker API - RapidAPI Listing

## Short Description
PII Redaction & Text Anonymization API for AI pipelines

## Long Description

### What is Masker?

Masker is a high-performance PII (Personally Identifiable Information) redaction API designed for AI/ML pipelines. It automatically detects and masks sensitive entities like names, emails, phones, and credit card numbers in both plain text and JSON structures.

### Why Use Masker?

**🔒 Privacy-First**
- Stateless design - no data storage or logging
- GDPR/CCPA compliant
- Process sensitive data safely before sending to LLMs

**⚡ High Performance**
- Sub-100ms response times
- Handles both text and JSON
- Batch processing support

**🎯 Accurate Detection**
- Regex patterns for structured PII (emails, phones, cards)
- spaCy NER for person name detection
- Multi-language support (English, Russian)

### Supported PII Types

| Type | Example | Detection |
|------|---------|-----------|
| EMAIL | john@example.com | Regex |
| PHONE | +1-555-123-4567 | Regex |
| CARD | 4111-1111-1111-1111 | Regex + Luhn |
| PERSON | John Doe | NER |

### Redaction Modes

- **mask** → `Contact ***` (default)
- **placeholder** → `Contact <EMAIL>`
- **redact** → `Contact [REDACTED]`

### Use Cases

1. **LLM Data Cleaning** - Strip PII before sending prompts to ChatGPT/Claude
2. **Log Anonymization** - Redact user data from application logs
3. **Analytics Preprocessing** - Anonymize data for GDPR compliance
4. **Document Processing** - Batch redact PDFs, CSVs, JSON files

---

## Category
Data > Text Processing

## Tags
pii, pii-detection, pii-redaction, privacy, anonymization, gdpr, compliance, llm, text-processing, data-cleaning

---

## Pricing Tiers

### Basic (Free)
- **Price:** $0/month
- **Requests:** 100/month
- **Rate Limit:** 10 requests/minute
- **Features:** All endpoints, Email support

### Pro
- **Price:** $9/month
- **Requests:** 10,000/month
- **Rate Limit:** 100 requests/minute
- **Features:** Priority support

### Ultra
- **Price:** $29/month
- **Requests:** 50,000/month
- **Rate Limit:** 500 requests/minute
- **Features:** Priority support, Webhook notifications

### Mega (Enterprise)
- **Price:** $99/month
- **Requests:** 250,000/month
- **Rate Limit:** 2,000 requests/minute
- **Features:** Dedicated support, Custom SLAs

---

## API Endpoints

### POST /v1/redact
Redact PII from text or JSON.

**Example Request:**
```bash
curl -X POST "https://masker-api.p.rapidapi.com/v1/redact" \
  -H "X-RapidAPI-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Email john@example.com", "mode": "mask"}'
```

**Example Response:**
```json
{
  "text": "Email ***",
  "entities": [
    {"type": "EMAIL", "redacted": "***", "start": 6, "end": 22}
  ],
  "processing_time_ms": 45.2
}
```

### GET /health
Health check endpoint.

---

## Support

- **Documentation:** https://github.com/KikuAI-Lab/masker/wiki
- **GitHub:** https://github.com/KikuAI-Lab/masker
- **Email:** support@kikuai.dev

---

## Terms & Privacy

- **Terms of Service:** https://kikuai.dev/legal/terms
- **Privacy Policy:** https://kikuai.dev/legal/privacy
- **License:** AGPL-3.0
