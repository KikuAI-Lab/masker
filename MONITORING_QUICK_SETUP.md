# Quick Monitoring Setup Guide

## Option 1: UptimeRobot (Recommended - Free Tier Available)

### Step 1: Create Account
1. Go to https://uptimerobot.com
2. Sign up for free account (50 monitors, 5-minute intervals)
3. Verify email

### Step 2: Add Monitors

#### Health Check Monitor
1. Click "Add New Monitor"
2. Configure:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** Masker API - Health Check
   - **URL:** `https://masker.kikuai.dev/health`
   - **Monitoring Interval:** 5 minutes
   - **Alert Contacts:** Select your email
3. Click "Create Monitor"

#### Main API Endpoint Monitor
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

#### SSL Certificate Monitor
1. Click "Add New Monitor"
2. Configure:
   - **Monitor Type:** SSL
   - **Friendly Name:** Masker API - SSL Certificate
   - **URL:** `masker.kikuai.dev`
   - **Alert When Expires In:** 30 days
   - **Alert Contacts:** Select your email
3. Click "Create Monitor"

### Step 3: Configure Alerts
1. Go to Settings > Alert Contacts
2. Add your email address
3. Verify email
4. Assign alert contacts to monitors

### Step 4: Test Alerts
1. Temporarily stop the API: `docker stop masker`
2. Wait for alert (should arrive within 5 minutes)
3. Restart API: `docker start masker`

---

## Option 2: Automated Setup (Using Script)

If you have UptimeRobot API key:

```bash
# Get API key from: https://uptimerobot.com/api/
export UPTIMEROBOT_API_KEY='your-api-key'

# Run setup script
./scripts/setup_monitoring.sh
```

---

## Option 3: Other Services

### Pingdom
- Free trial: 30 days
- URL: https://www.pingdom.com
- Similar setup process

### StatusCake
- Free tier: Unlimited tests, 5-minute intervals
- URL: https://www.statuscake.com
- Similar setup process

---

## Monitoring Checklist

- [ ] Health check monitor configured
- [ ] Main API endpoint monitor configured
- [ ] SSL certificate monitor configured
- [ ] Email alerts configured
- [ ] Slack alerts configured (optional)
- [ ] Alerts tested
- [ ] Dashboard created (optional)

---

## Current Status

**API URL:** https://masker.kikuai.dev  
**Health Check:** https://masker.kikuai.dev/health  
**Status:** ✅ Running and healthy

---

For detailed instructions, see: `docs/MONITORING_SETUP.md`

