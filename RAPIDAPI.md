# Masker - PII Redaction & Anonymization API

**Protect user privacy and comply with GDPR/CCPA by redacting personally identifiable information (PII) from text and JSON before sending it to LLMs or third-party services.**

---

## 🚀 Key Features

- **Privacy-First**: Stateless processing, no data storage, no content logging.
- **Multi-Mode**: Support for plain text and complex JSON structures.
- **Flexible Redaction**: Choose between masking (`***`) or placeholders (`<PERSON>`).
- **Entity Filtering**: Select exactly which PII types to redact.
- **Multi-Language**: Optimized for English and Russian.
- **High Performance**: < 20ms response time for typical payloads.

---

## 🛠️ Supported PII Types

| Type | Description | Detection Method |
|------|-------------|------------------|
| `EMAIL` | Email addresses | Regex (100% accuracy) |
| `PHONE` | International phone numbers | Regex (100% accuracy) |
| `CARD` | Credit/debit card numbers | Regex + Luhn check |
| `PERSON` | Person names | AI/NER (spaCy) |

---

## 💻 Usage Examples

### Python (using `requests`)

```python
import requests

url = "https://masker-api.p.rapidapi.com/v1/redact"

payload = {
    "text": "Contact John Doe at john@example.com",
    "mode": "placeholder",
    "entities": ["EMAIL", "PERSON"]
}

headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "YOUR_API_KEY",
	"X-RapidAPI-Host": "masker-api.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

**Response:**
```json
{
  "redacted_text": "Contact <PERSON> at <EMAIL>",
  "items": [
    {"entity_type": "PERSON", "start": 8, "end": 16, "score": 0.85},
    {"entity_type": "EMAIL", "start": 20, "end": 36, "score": 1.0}
  ],
  "processing_time_ms": 15.2
}
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const options = {
  method: 'POST',
  url: 'https://masker-api.p.rapidapi.com/v1/redact',
  headers: {
    'content-type': 'application/json',
    'X-RapidAPI-Key': 'YOUR_API_KEY',
    'X-RapidAPI-Host': 'masker-api.p.rapidapi.com'
  },
  data: {
    json: {
      user: {
        name: "John Doe",
        email: "john@example.com"
      }
    },
    mode: "mask"
  }
};

try {
	const response = await axios.request(options);
	console.log(response.data);
} catch (error) {
	console.error(error);
}
```

**Response:**
```json
{
  "redacted_json": {
    "user": {
      "name": "***",
      "email": "***"
    }
  },
  "processing_time_ms": 12.5
}
```

---

## 🔒 Security & Limits

- **Rate Limit**: 60 requests per minute per IP.
- **Payload Limit**: 64KB per request.
- **Data Retention**: Zero. Data is processed in memory and discarded immediately.

---

## 📦 Pricing

| Tier | Requests/Month | Rate Limit | Price |
|------|----------------|------------|-------|
| **Basic** | 100 | 1 req/sec | Free |
| **Pro** | 10,000 | 10 req/sec | $9.99 |
| **Ultra** | 100,000 | 50 req/sec | $49.99 |
| **Mega** | Unlimited | 100 req/sec | $199.99 |

---

## 📞 Support

For issues, feature requests, or enterprise plans, please contact us via RapidAPI messaging or open an issue on our GitHub repository.
