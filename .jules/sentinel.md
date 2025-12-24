## 2025-12-24 - Rate Limit Bypass via IP Spoofing
**Vulnerability:** The rate limiting middleware manually parsed `X-Forwarded-For` and `X-Real-IP` headers to determine the client IP. This allowed attackers to spoof their IP address by supplying a fake `X-Forwarded-For` header, bypassing the rate limits.
**Learning:** Manual parsing of proxy headers is dangerous. Applications should rely on the web server or ASGI server (like Uvicorn/Gunicorn) to handle proxy headers securely. Uvicorn, for example, has `--proxy-headers` and `--forwarded-allow-ips` options to trust specific upstream proxies.
**Prevention:**
1. Avoid manual parsing of `X-Forwarded-For` in application code.
2. Use `request.client.host` provided by Starlette/FastAPI, which is populated securely by the ASGI server.
3. Configure the deployment environment (Uvicorn/Nginx) to handle proxy headers and trust only known proxies.
4. If manual parsing is absolutely necessary (e.g. complex multi-proxy setup not supported by server), validate the upstream IP against a strict allowlist of trusted proxies.
