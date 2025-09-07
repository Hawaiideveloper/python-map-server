#!/bin/bash

# Test MCP Server Connection
echo "🧪 Testing MCP Server Connection"
echo "==============================="

NAMESPACE="python-mcp-server"
SERVICE_NAME="python-mcp-server-service"

# Get service information
echo "🔍 Getting service information..."
SERVICE_IP=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
SERVICE_PORT=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)

if [ -z "$SERVICE_IP" ] || [ "$SERVICE_IP" = "<pending>" ]; then
    echo "⚠️  LoadBalancer external IP not available, using port-forward..."
    kubectl port-forward svc/$SERVICE_NAME 8080:80 -n $NAMESPACE &
    PORT_FORWARD_PID=$!
    sleep 3
    MCP_URL="http://localhost:8080"
else
    MCP_URL="http://$SERVICE_IP:$SERVICE_PORT"
fi

echo "🎯 Testing MCP Server at: $MCP_URL"
echo ""

# Test health endpoint
echo "1️⃣ Testing health endpoint..."
if curl -s "$MCP_URL/health" >/dev/null 2>&1; then
    echo "✅ Health endpoint is responding"
    curl -s "$MCP_URL/health" | jq . 2>/dev/null || curl -s "$MCP_URL/health"
else
    echo "❌ Health endpoint is not responding"
fi

echo ""

# Test root endpoint
echo "2️⃣ Testing root endpoint..."
if curl -s "$MCP_URL/" >/dev/null 2>&1; then
    echo "✅ Root endpoint is responding"
    curl -s "$MCP_URL/" | head -5
else
    echo "❌ Root endpoint is not responding"
fi

echo ""

# Test MCP endpoint
echo "3️⃣ Testing MCP endpoint..."
if curl -s "$MCP_URL/mcp" >/dev/null 2>&1; then
    echo "✅ MCP endpoint is responding"
    curl -s "$MCP_URL/mcp" | head -5
else
    echo "❌ MCP endpoint is not responding"
fi

echo ""

# Test WebSocket endpoint
echo "4️⃣ Testing WebSocket endpoint..."
if curl -s "$MCP_URL/ws" >/dev/null 2>&1; then
    echo "✅ WebSocket endpoint is responding"
else
    echo "❌ WebSocket endpoint is not responding"
fi

echo ""

# Test tools endpoint
echo "5️⃣ Testing tools endpoint..."
if curl -s "$MCP_URL/tools" >/dev/null 2>&1; then
    echo "✅ Tools endpoint is responding"
    curl -s "$MCP_URL/tools" | jq . 2>/dev/null || curl -s "$MCP_URL/tools" | head -5
else
    echo "❌ Tools endpoint is not responding"
fi

echo ""
echo "🎉 MCP Server Connection Test Complete!"
echo "======================================"

# Clean up port forwarding if we started it
if [ ! -z "$PORT_FORWARD_PID" ]; then
    echo "🔄 Stopping port forwarding..."
    kill $PORT_FORWARD_PID 2>/dev/null
fi