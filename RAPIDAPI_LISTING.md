# RapidAPI Listing Content

## Long Description
**Your data is naked. Mask it.**

Every time you send customer data to a public LLM, you risk a leak. Names, emails, credit card numbers—once they leave your server, you lose control.

**Masker** is the firewall for your AI pipeline. It detects and obliterates sensitive PII entities in real-time, effectively anonymizing your prompts without breaking their context.

### Why Masker?
*   **0% Retention:** We are stateless. Your data is processed in RAM and forgotten instantly.
*   **High Velocity:** Built for high-throughput pipelines. <50ms latency P95.
*   **Context Aware:** Unlike regex, our NER models understand context, distinguishing between a dollar amount and a credit card number.

### Core Features
*   **Smart Redaction:** Replace PII with tokenized placeholders (e.g., `[EMAIL]`, `[PERSON]`) so LLMs can still understand the sentence structure.
*   **JSON Support:** Submit complex JSON objects, and we'll recursively walk the tree to mask values while preserving keys and structure.
*   **Multi-Language:** Strong support for English and Russian text.

**Stop feeding your secrets to the machine. Use Masker.**

---

## Terms of Use

By using the Masker API ("Service"), you agree to the following terms:

**1. No Malicious Use**
You may not use the Service to:
*   De-anonymize or re-identify individuals from redacted data.
*   Process data you do not have permission to handle.
*   Reverse engineer the underlying models or API logic.

**2. Data Privacy & Statelessness**
The Service is **stateless**. We process your input text solely for the purpose of redaction and do not store, log, or train on your payloads. Once the response is returned, your data is wiped from our memory.

**3. Disclaimer of Warranty**
The Service is provided "AS IS". While we strive for high accuracy (>95% F1-score), no automated PII detection system is perfect. You remain largely responsible for ensuring your data compliance (GDPR, CCPA, HIPAA). We are not liable for any missed PII entities or subsequent data leaks.

**4. Fair Use**
We reserve the right to throttle or terminate API keys that exhibit abusive behavior, consistent errors, or attempts to bypass rate limits.

**5. Changes**
We may update these terms or the API pricing at any time. Continued use signifies acceptance of the new terms.
