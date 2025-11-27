#!/bin/bash
# Setup monitoring for Masker API
# This script helps set up monitoring using UptimeRobot API

set -e

API_URL="https://masker.kikuai.dev"
HEALTH_ENDPOINT="${API_URL}/health"
MAIN_ENDPOINT="${API_URL}/v1/redact"

echo "🔍 Masker API Monitoring Setup"
echo "================================"
echo ""

# Check if UPTIMEROBOT_API_KEY is set
if [ -z "$UPTIMEROBOT_API_KEY" ]; then
    echo "⚠️  UPTIMEROBOT_API_KEY environment variable is not set."
    echo ""
    echo "To get your API key:"
    echo "1. Go to https://uptimerobot.com"
    echo "2. Sign up or log in"
    echo "3. Go to My Settings > API Settings"
    echo "4. Create a new API key"
    echo ""
    echo "Then run:"
    echo "  export UPTIMEROBOT_API_KEY='your-api-key'"
    echo "  ./scripts/setup_monitoring.sh"
    echo ""
    exit 1
fi

echo "✅ API Key found"
echo ""

# Function to create monitor
create_monitor() {
    local name=$1
    local url=$2
    local type=$3
    local keyword=$4
    
    echo "Creating monitor: $name"
    
    if [ -n "$keyword" ]; then
        # Keyword monitor (for POST endpoints)
        response=$(curl -s -X POST "https://api.uptimerobot.com/v2/newMonitor" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "api_key=${UPTIMEROBOT_API_KEY}" \
            -d "format=json" \
            -d "type=2" \
            -d "url=${url}" \
            -d "friendly_name=${name}" \
            -d "keyword_type=1" \
            -d "keyword_value=${keyword}" \
            -d "interval=300")
    else
        # HTTP monitor
        response=$(curl -s -X POST "https://api.uptimerobot.com/v2/newMonitor" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "api_key=${UPTIMEROBOT_API_KEY}" \
            -d "format=json" \
            -d "type=1" \
            -d "url=${url}" \
            -d "friendly_name=${name}" \
            -d "interval=300")
    fi
    
    if echo "$response" | grep -q '"stat":"ok"'; then
        echo "  ✅ Monitor created successfully"
    else
        echo "  ❌ Failed to create monitor"
        echo "  Response: $response"
    fi
    echo ""
}

# Create monitors
echo "Creating monitors..."
echo ""

# 1. Health Check Monitor
create_monitor "Masker API - Health Check" "$HEALTH_ENDPOINT" "1" ""

# 2. Main API Endpoint Monitor (keyword-based for POST)
create_monitor "Masker API - Main Endpoint" "$MAIN_ENDPOINT" "2" "redacted_text"

# 3. SSL Certificate Monitor
create_monitor "Masker API - SSL Certificate" "$API_URL" "4" ""

echo "✅ Monitoring setup complete!"
echo ""
echo "Next steps:"
echo "1. Go to https://uptimerobot.com/dashboard"
echo "2. Verify all monitors are created"
echo "3. Configure alert contacts (Settings > Alert Contacts)"
echo "4. Set up email/Slack notifications"
echo ""

