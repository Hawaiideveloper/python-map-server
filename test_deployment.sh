#!/bin/bash

# Railway WebSocket Deployment Test Script

BASE_URL="https://python-mcp-server-production.up.railway.app"
ADMIN_KEY="mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs"

echo "🚀 Testing Railway Deployment"
echo "=================================================="

echo ""
echo "1. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -w "%{http_code}" -H "X-Admin-Key: $ADMIN_KEY" "$BASE_URL/health")
HTTP_CODE="${HEALTH_RESPONSE: -3}"
HEALTH_BODY="${HEALTH_RESPONSE%???}"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Health check passed"
    echo "$HEALTH_BODY" | jq -r '"Version: " + .version + " - Status: " + .status'
else
    echo "❌ Health check failed: HTTP $HTTP_CODE"
    exit 1
fi

echo ""
echo "2. Testing for WebSocket protocol support..."
ROOT_RESPONSE=$(curl -s -w "%{http_code}" -H "X-Admin-Key: $ADMIN_KEY" "$BASE_URL/")
HTTP_CODE="${ROOT_RESPONSE: -3}"
ROOT_BODY="${ROOT_RESPONSE%???}"

if [ "$HTTP_CODE" = "200" ]; then
    # Check if protocols field exists
    PROTOCOLS=$(echo "$ROOT_BODY" | jq -r '.protocols // empty')
    if [ -n "$PROTOCOLS" ]; then
        echo "✅ WebSocket protocols found:"
        echo "$ROOT_BODY" | jq -r '.protocols[] | "   - " + .name + ": " + .url'
        echo ""
        echo "🎉 WebSocket MCP support is DEPLOYED!"
        echo "=================================================="
        echo ""
        echo "📋 CONNECTION DETAILS:"
        echo "HTTP API: $BASE_URL"
        echo "WebSocket MCP: ws://${BASE_URL#https://}/mcp"
        echo "Admin Key: $ADMIN_KEY"
        echo ""
        echo "📖 For usage instructions, see: MCP_WEBSOCKET_GUIDE.md"
        exit 0
    else
        echo "⚠️  No 'protocols' field found - WebSocket support not yet deployed"
        echo "Current response:"
        echo "$ROOT_BODY" | jq '.'
    fi
else
    echo "❌ Root endpoint failed: HTTP $HTTP_CODE"
    exit 1
fi

echo ""
echo "3. Triggering redeploy..."
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "Deployment triggered at: $TIMESTAMP" > deployment_trigger.txt

git add deployment_trigger.txt
git commit -m "Trigger deployment for WebSocket support - $TIMESTAMP"
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Git push successful - Railway should auto-deploy"
    echo ""
    echo "4. Monitoring deployment progress..."
    echo "   Please wait 2-3 minutes for Railway to build and deploy..."
    echo "   Then run this script again to verify WebSocket support."
else
    echo "❌ Git push failed"
    exit 1
fi
