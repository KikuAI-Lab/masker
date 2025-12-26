# The Stateless PII Engine

Masker is built with a single, uncompromising principle: **Zero Data Retention.**

We understand that you are trusting us with your most sensitive customer data. Our architecture is designed to make it technically impossible for us to leak, sell, or store your data—because we simply don't have it.

## 1. Stateless by Design
Most APIs store payloads in a database for analytics, debugging, or future model training. **We do not.**

*   **No Database for Payloads:** Use of persistent storage (PostgreSQL/Redis) is strictly limited to API keys, rate limits, and anonymized usage counters.
*   **RAM-Only Processing:** Your text payload enters our memory, is processed by the reduction engine, and is immediately discarded once the HTTP response is sent.
*   **0% Logs:** Our logging level is configured to strictly exclude request bodies. Even in the event of a crash, your PII does not end up in our error logs.

## 2. Local Intelligence (No 3rd Party LLMs)
Masker does **not** forward your data to OpenAI, Anthropic, or any other third-party AI provider.

*   **Local Models:** We utilize optimized, local NLP models (based on spaCy and transformer architectures) that run entirely within our isolated containers.
*   **Air-Gapped Logic:** The PII detection logic does not require internet access to function.
*   **Consistent Latency:** By avoiding external API calls, we guarantee P95 latency under 50ms, unaffected by "AI hype" traffic spikes.

## 3. The "Firewall" Metaphor
Think of Masker not as a storage bucket, but as a firewall.
Traffic passes *through* it, gets filtered, and continues to your destination (e.g., ChatGPT). The firewall doesn't keep a copy of your packets. Neither do we.

## 4. Enterprise Self-Hosting
For organizations with strict data residency requirements (GDPR, HIPAA) who require a literal air-gap:

Masker is available as a Docker container that you can deploy in your own VPC.
*   **No external calls.**
*   **Full control over infrastructure.**
*   [Contact us](mailto:support@kikuai.dev) for an Enterprise License.
