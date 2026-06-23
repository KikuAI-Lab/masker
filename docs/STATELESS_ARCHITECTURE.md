# The Stateless PII Engine

Masker is built around a narrow principle: avoid storing raw user payloads.

The architecture is designed so request bodies are processed in memory and are
not intentionally persisted by the service. Deployment logs, reverse proxies,
crash dumps, and upstream providers still need to be configured and reviewed by
the operator.

## 1. Stateless by Design
Many APIs store payloads in a database for analytics, debugging, or future model
training. Masker is designed not to persist raw payloads.

*   **No Database for Payloads:** Use of persistent storage (PostgreSQL/Redis) is strictly limited to API keys, rate limits, and anonymized usage counters.
*   **RAM-Only Processing:** Your text payload enters our memory, is processed by the reduction engine, and is immediately discarded once the HTTP response is sent.
*   **No Request-Body Logging by Design:** Application logging is configured to exclude request bodies. Operators should also review platform, proxy, and crash logging.

## 2. Local Intelligence (No 3rd Party LLMs)
The local redaction path does **not** forward data to OpenAI, Anthropic, or any
other third-party AI provider.

*   **Local Models:** We utilize optimized, local NLP models (based on spaCy and transformer architectures) that run entirely within our isolated containers.
*   **Self-Hosted Detection:** The PII detection logic does not require internet access to function.
*   **Predictable Latency Boundary:** Avoiding external detection calls removes provider latency from the redaction path. Actual latency depends on hardware, payload size, model choice, and deployment configuration.

## 3. The "Firewall" Metaphor
Think of Masker not as a storage bucket, but as a firewall.
Traffic passes *through* it, gets filtered, and continues to your destination
when proxy mode is enabled. The service is designed not to keep a raw copy of
the payload.

## 4. Enterprise Self-Hosting
For organizations with strict data residency requirements (GDPR, HIPAA) who require a literal air-gap:

Masker is available as a Docker container that you can deploy in your own VPC.
*   **No external calls for local PII detection.**
*   **Full control over infrastructure.**
*   [Contact us](mailto:support@kikuai.dev) for an Enterprise License.
