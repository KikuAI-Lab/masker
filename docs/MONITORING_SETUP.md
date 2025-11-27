# Monitoring Setup Guide

Complete guide for setting up monitoring and alerts for Masker API.

---

## 🎯 Recommended Monitoring Services

### 1. UptimeRobot (Free Tier Available)
- **Free:** 50 monitors, 5-minute intervals
- **Paid:** $7/month for 1-minute intervals
- **URL:** https://uptimerobot.com

### 2. Pingdom
- **Free Trial:** 30 days
- **Paid:** Starting at $10/month
- **URL:** https://www.pingdom.com

### 3. StatusCake
- **Free:** Unlimited tests, 5-minute intervals
- **Paid:** Starting at $20/month
- **URL:** https://www.statuscake.com

---

## 📊 What to Monitor

### Critical Endpoints

1. **Health Check**
   - URL: `https://masker.kikuai.dev/health`
   - Expected: HTTP 200, `{"status":"ok"}`
   - Interval: 1-5 minutes

2. **Main API Endpoint**
   - URL: `https://masker.kikuai.dev/v1/redact`
   - Method: POST
   - Body: `{"text": "test@example.com", "mode": "placeholder"}`
   - Expected: HTTP 200, contains `"redacted_text"`
   - Interval: 5 minutes

3. **SSL Certificate**
   - URL: `https://masker.kikuai.dev`
   - Check: SSL expiration
   - Alert: 30 days before expiration

---

## 🔔 Alert Configuration

### Alert Channels

1. **Email** (Required)
   - Send to: Your email address
   - Frequency: Immediate on failure

2. **Slack** (Recommended)
   - Webhook URL: Your Slack webhook
   - Channel: #alerts or #monitoring

3. **SMS** (Optional)
   - For critical alerts only
   - Use sparingly to avoid alert fatigue

### Alert Conditions

**Critical Alerts:**
- API is down (HTTP 5xx or timeout)
- Health check fails
- SSL certificate expires in < 30 days

**Warning Alerts:**
- Response time > 500ms
- Error rate > 5%
- SSL certificate expires in < 60 days

---

## 🛠️ UptimeRobot Setup (Step-by-Step)

### Step 1: Create Account
1. Go to https://uptimerobot.com
2. Sign up for free account
3. Verify email

### Step 2: Add Health Check Monitor

1. Click "Add New Monitor"
2. Configure:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** Masker API - Health Check
   - **URL:** `https://masker.kikuai.dev/health`
   - **Monitoring Interval:** 5 minutes
   - **Alert Contacts:** Select your email
3. Click "Create Monitor"

### Step 3: Add API Endpoint Monitor

1. Click "Add New Monitor"
2. Configure:
   - **Monitor Type:** Keyword
   - **Friendly Name:** Masker API - Main Endpoint
   - **URL:** `https://masker.kikuai.dev/v1/redact`
   - **HTTP Method:** POST
   - **HTTP Body:** `{"text": "test@example.com", "mode": "placeholder"}`
   - **Keyword to Monitor:** `"redacted_text"`
   - **Monitoring Interval:** 5 minutes
   - **Alert Contacts:** Select your email
3. Click "Create Monitor"

### Step 4: Add SSL Monitor

1. Click "Add New Monitor"
2. Configure:
   - **Monitor Type:** SSL
   - **Friendly Name:** Masker API - SSL Certificate
   - **URL:** `masker.kikuai.dev`
   - **Alert When Expires In:** 30 days
   - **Alert Contacts:** Select your email
3. Click "Create Monitor"

---

## 📈 Metrics to Track

### Availability
- **Target:** 99.9% uptime
- **Measurement:** Successful health checks / Total checks

### Response Time
- **Target:** < 200ms average
- **Measurement:** Average `processing_time_ms` from responses

### Error Rate
- **Target:** < 1%
- **Measurement:** 4xx/5xx responses / Total responses

### SSL Certificate
- **Target:** Always valid
- **Measurement:** Days until expiration

---

## 🔍 Log Monitoring

### What to Monitor in Logs

1. **Error Frequency**
   - Count of 500 errors
   - Count of 400 errors (validation issues)

2. **Performance**
   - Requests with `processing_time_ms` > 500ms
   - Requests with `processing_time_ms` > 1000ms

3. **Request Patterns**
   - Unusual spike in requests
   - Requests from specific IPs

### Log Analysis Commands

```bash
# Check recent errors
docker logs masker --tail 100 | grep "status=5"

# Check slow requests
docker logs masker --tail 100 | grep "duration_ms" | awk '$NF > 500'

# Check request count
docker logs masker --tail 1000 | grep "request:" | wc -l
```

---

## 📊 Dashboard Setup

### Recommended Tools

1. **Grafana** (if using Prometheus)
   - Create dashboards for:
     - Request rate
     - Response time
     - Error rate
     - Availability

2. **UptimeRobot Dashboard**
   - Public status page
   - Share with users

### Key Metrics Dashboard

Create a dashboard showing:
- Current uptime percentage
- Average response time (last 24h)
- Error rate (last 24h)
- Request count (last 24h)
- SSL certificate expiration date

---

## 🚨 Alert Examples

### Email Alert Template

**Subject:** [CRITICAL] Masker API is Down

**Body:**
```
Alert: Masker API Health Check Failed

Endpoint: https://masker.kikuai.dev/health
Status: HTTP 502
Time: 2025-11-27 10:30:00 UTC
Duration: 5 minutes

Action Required:
1. Check server status: ssh root@37.27.38.186
2. Check Docker container: docker ps | grep masker
3. Check logs: docker logs masker --tail 50
4. Restart if needed: docker restart masker
```

### Slack Alert Template

```json
{
  "text": "🚨 *Masker API Alert*",
  "attachments": [
    {
      "color": "danger",
      "fields": [
        {
          "title": "Status",
          "value": "DOWN",
          "short": true
        },
        {
          "title": "Endpoint",
          "value": "https://masker.kikuai.dev/health",
          "short": true
        },
        {
          "title": "Time",
          "value": "2025-11-27 10:30:00 UTC",
          "short": true
        }
      ]
    }
  ]
}
```

---

## ✅ Monitoring Checklist

- [ ] Health check monitor configured
- [ ] Main API endpoint monitor configured
- [ ] SSL certificate monitor configured
- [ ] Email alerts configured
- [ ] Slack alerts configured (optional)
- [ ] Alert thresholds set appropriately
- [ ] Dashboard created (optional)
- [ ] Public status page created (optional)
- [ ] Log monitoring set up
- [ ] Response time tracking enabled

---

## 🔧 Maintenance

### Weekly Tasks
- Review alert history
- Check for false positives
- Adjust alert thresholds if needed

### Monthly Tasks
- Review uptime statistics
- Analyze error patterns
- Optimize based on metrics

---

## 📞 Support Contacts

If monitoring detects issues:
1. Check server status first
2. Review logs for errors
3. Check SSL certificate status
4. Contact hosting provider if needed

---

**Last Updated:** 2025-11-27

