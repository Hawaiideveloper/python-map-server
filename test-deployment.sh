#!/bin/bash

# Script to test the deployed python-mcp-server
echo "🧪 Testing python-mcp-server Deployment"
echo "====================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Check deployment status
echo "📋 Deployment status:"
kubectl get pods -n python-mcp-server
kubectl get svc -n python-mcp-server

echo ""
echo "🔍 Service endpoints:"
kubectl get endpoints python-mcp-server-service -n python-mcp-server

echo ""
echo "🌐 LoadBalancer status:"
kubectl get svc python-mcp-server-service -n python-mcp-server -o wide

echo ""
echo "🔗 Testing service connectivity..."
echo "Starting port-forward (this will run in background)..."
kubectl port-forward svc/python-mcp-server-service 8080:80 -n python-mcp-server &
PORT_FORWARD_PID=$!

# Wait for port-forward to start
sleep 5

echo ""
echo "🧪 Testing health endpoint..."
curl -s http://localhost:8080/health || echo "❌ Health check failed"

echo ""
echo "🧪 Testing root endpoint..."
curl -s http://localhost:8080/ || echo "❌ Root endpoint failed"

echo ""
echo "🧪 Testing API endpoints..."
curl -s http://localhost:8080/api/health || echo "❌ API health check failed"

echo ""
echo "🧪 Testing MCP endpoints..."
curl -s http://localhost:8080/mcp/health || echo "❌ MCP health check failed"

# Stop port-forward
echo ""
echo "🛑 Stopping port-forward..."
kill $PORT_FORWARD_PID 2>/dev/null

echo ""
echo "🎉 Testing complete!"
echo ""
echo "📝 Service Information:"
echo "   Namespace: python-mcp-server"
echo "   Service: python-mcp-server-service"
echo "   Type: LoadBalancer"
echo "   Port: 80 -> 8080"
echo ""
echo "🔗 To access the service:"
echo "   kubectl port-forward svc/python-mcp-server-service 8080:80 -n python-mcp-server"
echo "   Then visit: http://localhost:8080"