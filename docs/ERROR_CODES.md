# Error Codes Reference

Complete reference for all error codes returned by Masker API.

---

## HTTP Status Codes

### 200 OK
Request successful.

**Response:**
```json
{
  "redacted_text": "...",
  "items": [...],
  "processing_time_ms": 15.29
}
```

---

### 400 Bad Request
Invalid request format or validation error.

**Response:**
```json
{
  "detail": "Error description"
}
```

**Common Errors:**

#### Missing Input
```json
{
  "detail": "body: Value error, Either 'text' or 'json' must be provided"
}
```
**Solution:** Provide either `text` or `json` field in request body.

#### Empty Text
```json
{
  "detail": "body -> text: String should have at least 1 character"
}
```
**Solution:** Provide non-empty text string.

#### Invalid Mode
```json
{
  "detail": "body -> mode: Input should be 'mask' or 'placeholder'"
}
```
**Solution:** Use `"mask"` or `"placeholder"` as mode value.

#### Invalid Entity Type
```json
{
  "detail": "body -> entities -> 0: Input should be 'PERSON', 'EMAIL', 'PHONE' or 'CARD'"
}
```
**Solution:** Use only valid entity types: `PERSON`, `EMAIL`, `PHONE`, `CARD`.

#### Invalid Language
```json
{
  "detail": "body -> language: Input should be 'en' or 'ru'"
}
```
**Solution:** Use `"en"` or `"ru"` as language value.

#### Both Text and JSON Provided
```json
{
  "detail": "body: Value error, Cannot provide both 'text' and 'json'"
}
```
**Solution:** Provide only one: either `text` OR `json`, not both.

---

### 413 Payload Too Large
Request body exceeds size limit.

**Response:**
```json
{
  "detail": "Request body too large. Maximum allowed payload size is 65536 bytes (64KB)."
}
```

**Limits:**
- Text field: 32KB (32,768 bytes)
- Total JSON payload: 64KB (65,536 bytes)

**Solution:**
- Split large text into smaller chunks
- Reduce JSON payload size
- Remove unnecessary data

---

### 429 Too Many Requests
Rate limit exceeded.

**Response:**
```json
{
  "detail": "Too many requests. Please try again later."
}
```

**Rate Limits:**
- Free tier: 10 requests/minute, 100/day
- Basic tier: 100 requests/minute, 10,000/month
- Pro tier: 500 requests/minute, 100,000/month

**Solution:**
- Wait before making more requests
- Implement exponential backoff
- Upgrade to higher tier if needed

---

### 500 Internal Server Error
Unexpected server error.

**Response:**
```json
{
  "detail": "Internal server error"
}
```

**Solution:**
- Retry the request after a short delay
- Check API status at `/health`
- Contact support if error persists

---

## Error Handling Examples

### Python
```python
import requests
import time

def redact_with_retry(text, max_retries=3):
    url = "https://masker.kikuai.dev/v1/redact"
    headers = {
        "X-RapidAPI-Key": "YOUR_KEY",
        "Content-Type": "application/json"
    }
    data = {"text": text, "mode": "placeholder"}
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limit - wait and retry
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                continue
            elif response.status_code == 413:
                # Payload too large
                raise ValueError("Text is too large. Maximum 32KB.")
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    
    raise Exception("Max retries exceeded")
```

### JavaScript
```javascript
const axios = require('axios');

async function redactWithRetry(text, maxRetries = 3) {
  const url = 'https://masker.kikuai.dev/v1/redact';
  const headers = {
    'X-RapidAPI-Key': 'YOUR_KEY',
    'Content-Type': 'application/json'
  };
  const data = { text, mode: 'placeholder' };
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await axios.post(url, data, { headers });
      
      if (response.status === 200) {
        return response.data;
      } else if (response.status === 429) {
        // Rate limit - wait and retry
        const waitTime = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, waitTime));
        continue;
      } else if (response.status === 413) {
        throw new Error('Text is too large. Maximum 32KB.');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.data.detail}`);
      }
    } catch (error) {
      if (attempt === maxRetries - 1) {
        throw error;
      }
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
    }
  }
  
  throw new Error('Max retries exceeded');
}
```

---

## Troubleshooting

### Issue: "Either 'text' or 'json' must be provided"
**Cause:** Request body is missing both `text` and `json` fields.

**Fix:** Add either `text` or `json` to your request:
```json
{
  "text": "Your text here"
}
```

### Issue: "Request body too large"
**Cause:** Request exceeds 64KB limit.

**Fix:** 
- Split text into smaller chunks (< 32KB each)
- Reduce JSON payload size
- Process data in batches

### Issue: "Too many requests"
**Cause:** Rate limit exceeded.

**Fix:**
- Implement exponential backoff
- Reduce request frequency
- Upgrade to higher tier

### Issue: "Internal server error"
**Cause:** Unexpected server error.

**Fix:**
- Retry after a short delay
- Check `/health` endpoint
- Contact support if persists

---

## Status Code Summary

| Code | Meaning | Retry? | User Action |
|------|---------|--------|-------------|
| 200 | Success | No | Use response data |
| 400 | Bad Request | No | Fix request format |
| 413 | Payload Too Large | No | Reduce payload size |
| 429 | Too Many Requests | Yes | Wait and retry |
| 500 | Server Error | Yes | Retry or contact support |

---

**Last Updated:** 2025-11-27

