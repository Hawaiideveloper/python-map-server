#!/bin/bash

# Final Verification Script - Run when network is available
# Tests the complete Railway MCP Server deployment

echo "🎯 FINAL VERIFICATION - Python MCP Server on Railway"
echo "====================================================="

BASE_URL="https://python-mcp-server-production.up.railway.app"
ADMIN_KEY="mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs"

echo ""
echo "Server URL: $BASE_URL"
echo "Testing with admin authentication..."
echo ""

# Test 1: Health Check
echo "1. Health Check:"
curl -s -H "X-Admin-Key: $ADMIN_KEY" "$BASE_URL/health" | jq -r '"✅ Status: " + .status + " | Version: " + .version' || echo "❌ Health check failed"

echo ""
echo "2. WebSocket MCP Protocol:"
curl -s -H "X-Admin-Key: $ADMIN_KEY" "$BASE_URL/" | jq -r '.protocols | "✅ WebSocket: " + .mcp_websocket + "\n✅ HTTP: " + .http_rest' || echo "❌ Protocol check failed"

echo ""
echo "3. Python Code Execution:"
curl -s -X POST "$BASE_URL/run_code" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"✅ Python execution working on Railway!\")"}' | jq -r '.result.stdout' || echo "❌ Code execution failed"

echo ""
echo "4. System Intelligence:"
curl -s -X GET "$BASE_URL/system/info" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq -r '"✅ System: " + (.result.cpu.cpu_count | tostring) + " cores, " + (.result.memory.total_gb | tostring) + "GB RAM"' || echo "❌ System info failed"

echo ""
echo "5. MCP Tools Available:"
curl -s -H "X-Admin-Key: $ADMIN_KEY" "$BASE_URL/" | jq -r '.endpoints | to_entries | length | "✅ " + (. | tostring) + " HTTP endpoints available"' || echo "❌ Endpoints check failed"

echo ""
echo "====================================================="
echo "🎉 DEPLOYMENT VERIFICATION COMPLETE"
echo ""
echo "📋 CONNECTION DETAILS:"
echo "   WebSocket MCP: wss://python-mcp-server-production.up.railway.app/mcp"
echo "   HTTP REST API: https://python-mcp-server-production.up.railway.app"
echo "   Admin Key: $ADMIN_KEY"
echo ""
echo "📖 Documentation:"
echo "   Setup Guide: MCP_WEBSOCKET_GUIDE.md"
echo "   Success Report: DEPLOYMENT_SUCCESS.md"
echo "   API Docs: https://python-mcp-server-production.up.railway.app/docs"
