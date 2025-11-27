# Masker API - Complete API Reference

**Base URL:** `https://masker.kikuai.dev`  
**API Version:** 1.0.0

---

## Authentication

All requests require the `X-RapidAPI-Key` header:

```
X-RapidAPI-Key: YOUR_RAPIDAPI_KEY
```

---

## Endpoints

### POST /v1/redact

Main endpoint for PII redaction. Supports both text and JSON input modes.

**Request:**

```http
POST /v1/redact
Content-Type: application/json
X-RapidAPI-Key: YOUR_RAPIDAPI_KEY
```

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | One of text/json | - | Plain text to process (max 32KB) |
| `json` | object | One of text/json | - | JSON object/array to process (max 64KB total) |
| `mode` | string | No | `"mask"` | Redaction mode: `"mask"` or `"placeholder"` |
| `entities` | array | No | `null` | Filter specific entity types: `["PERSON", "EMAIL", "PHONE", "CARD"]` |
| `language` | string | No | `"en"` | Language code: `"en"` or `"ru"` |

**Request Examples:**

```json
// Text mode with placeholder
{
  "text": "Contact John Doe at john@example.com",
  "mode": "placeholder"
}

// JSON mode with entity filter
{
  "json": {
    "user": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  },
  "mode": "placeholder",
  "entities": ["EMAIL"]
}

// Mask mode (default)
{
  "text": "My card is 4111-1111-1111-1111",
  "mode": "mask"
}
```

**Response:**

```json
{
  "redacted_text": "string | null",
  "redacted_json": "object | null",
  "items": [
    {
      "entity_type": "PERSON | EMAIL | PHONE | CARD",
      "path": "string | null",
      "start": 0,
      "end": 8,
      "score": 0.85
    }
  ],
  "processing_time_ms": 15.29
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `redacted_text` | string \| null | Redacted text (null if JSON mode) |
| `redacted_json` | object \| null | Redacted JSON (null if text mode) |
| `items` | array | List of detected and redacted entities |
| `processing_time_ms` | number | Processing time in milliseconds |

**Item Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `entity_type` | string | Type of PII: `PERSON`, `EMAIL`, `PHONE`, `CARD` |
| `path` | string \| null | JSON path (null for text mode) |
| `start` | number | Start position in text |
| `end` | number | End position in text |
| `score` | number | Confidence score (0.0-1.0) |

**Response Examples:**

```json
// Text mode response
{
  "redacted_text": "Contact <PERSON> at <EMAIL>",
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
    }
  ],
  "processing_time_ms": 15.29
}

// JSON mode response
{
  "redacted_text": null,
  "redacted_json": {
    "user": {
      "name": "<PERSON>",
      "email": "<EMAIL>"
    }
  },
  "items": [
    {
      "entity_type": "PERSON",
      "path": "user.name",
      "start": 0,
      "end": 8,
      "score": 0.85
    },
    {
      "entity_type": "EMAIL",
      "path": "user.email",
      "start": 0,
      "end": 16,
      "score": 1.0
    }
  ],
  "processing_time_ms": 23.46
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 413 | Payload Too Large |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

### GET /health

Health check endpoint. No authentication required.

**Request:**

```http
GET /health
```

**Response:**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Service is healthy |

---

### GET /docs

Interactive API documentation (Swagger UI). No authentication required.

**Request:**

```http
GET /docs
```

---

### GET /openapi.json

OpenAPI 3.1.0 specification. No authentication required.

**Request:**

```http
GET /openapi.json
```

---

## Redaction Modes

### Mode: `mask`

Replaces PII with `***` (asterisks).

**Example:**
```json
Input:  "Contact john@example.com"
Output: "Contact ***"
```

### Mode: `placeholder`

Replaces PII with type-specific placeholders:
- `<PERSON>` for person names
- `<EMAIL>` for email addresses
- `<PHONE>` for phone numbers
- `<CARD>` for credit card numbers

**Example:**
```json
Input:  "Contact john@example.com"
Output: "Contact <EMAIL>"
```

---

## Entity Types

### PERSON
Person names detected using spaCy NER (Named Entity Recognition).

- **Languages:** English, Russian
- **Confidence:** ~0.85 average
- **Example:** "John Doe", "Иван Иванов"

### EMAIL
Email addresses detected using regex.

- **Confidence:** 1.0 (100%)
- **Example:** "john@example.com"

### PHONE
Phone numbers detected using regex (international formats).

- **Confidence:** 1.0 (100%)
- **Example:** "+1-555-123-4567", "+7 999 123 45 67"

### CARD
Credit/debit card numbers detected using regex with Luhn validation.

- **Confidence:** 1.0 (100%)
- **Example:** "4111-1111-1111-1111"

---

## Entity Filtering

Use the `entities` field to redact only specific PII types:

```json
{
  "text": "John Doe's email is john@example.com",
  "mode": "placeholder",
  "entities": ["EMAIL"]
}
```

**Result:** `"John Doe's email is <EMAIL>"`

Note: `PERSON` is not redacted because it's not in the filter.

If `entities` is not provided or is empty, all PII types are redacted.

---

## JSON Mode

JSON mode processes JSON structures recursively, only modifying string values:

```json
{
  "json": {
    "user": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30,
      "tags": ["developer", "john@example.com"]
    }
  },
  "mode": "placeholder"
}
```

**Result:**
```json
{
  "user": {
    "name": "<PERSON>",
    "email": "<EMAIL>",
    "age": 30,
    "tags": ["developer", "<EMAIL>"]
  }
}
```

**Notes:**
- Only string values are processed
- JSON structure is preserved
- Non-string values (numbers, booleans, null) are unchanged
- Arrays are processed recursively

---

## Error Responses

### 400 Bad Request

Invalid request format or validation error.

```json
{
  "detail": "body: Value error, Either 'text' or 'json' must be provided"
}
```

**Common causes:**
- Missing `text` or `json` field
- Both `text` and `json` provided
- Invalid `mode` value
- Invalid `entities` values
- Empty `text` field

### 413 Payload Too Large

Request body exceeds size limit.

```json
{
  "detail": "Request body too large. Maximum allowed payload size is 65536 bytes (64KB)."
}
```

**Limits:**
- Text field: 32KB
- Total payload: 64KB

### 429 Too Many Requests

Rate limit exceeded.

```json
{
  "detail": "Too many requests. Please try again later."
}
```

**Rate limits:**
- Free: 10 requests/minute
- Basic: 100 requests/minute
- Pro: 500 requests/minute

### 500 Internal Server Error

Server error.

```json
{
  "detail": "Internal server error"
}
```

Contact support if this error persists.

---

## Rate Limits

Rate limits are enforced by RapidAPI based on your subscription tier:

| Tier | Requests per Minute | Requests per Day/Month |
|------|---------------------|------------------------|
| Free | 10 | 100/day |
| Basic | 100 | 10,000/month |
| Pro | 500 | 100,000/month |
| Enterprise | Custom | Unlimited |

---

## Response Headers

All responses include:

| Header | Description |
|--------|-------------|
| `X-Request-ID` | Unique request identifier for tracking |
| `X-Processing-Time` | Processing time in milliseconds |
| `Content-Type` | `application/json` |

---

## Best Practices

1. **Always check response status** before using `redacted_text` or `redacted_json`
2. **Handle errors gracefully** - implement retry logic for 429 errors
3. **Use entity filtering** to improve performance when you only need specific types
4. **Cache results** when processing the same data multiple times
5. **Monitor processing time** using `processing_time_ms` for performance tracking

---

## Examples

See [Quick Start Guide](./QUICK_START.md) for complete examples.

---

**Last Updated:** 2025-11-27  
**API Version:** 1.0.0

