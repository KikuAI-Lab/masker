# SDK Examples

Usage examples for different programming languages.

## Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/v1/redact",
    json={"text": "john@example.com", "mode": "placeholder"}
)
print(response.json()["redacted_text"])  # <EMAIL>
```

## JavaScript

```javascript
const response = await fetch("http://localhost:8000/v1/redact", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: "john@example.com", mode: "placeholder" })
});
const data = await response.json();
console.log(data.redacted_text);  // <EMAIL>
```

## Files

| File | Language |
|------|----------|
| `python_example.py` | Python (httpx, OpenAI SDK) |
| `javascript_example.js` | JavaScript (fetch, node-fetch) |
