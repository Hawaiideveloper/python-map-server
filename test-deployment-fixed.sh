#!/bin/bash

# Script to test the deployed python-mcp-server with better port-forward handling
echo "🧪 Testing python-mcp-server Deployment (Fixed)"
echo "============================================="

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
echo "🔍 Pod port information:"
kubectl get pods -n python-mcp-server -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].ports[0].containerPort}{"\n"}{end}'

echo ""
echo "🔗 Testing with direct pod access..."
# Get the first pod name
POD_NAME=$(kubectl get pods -n python-mcp-server -l app=python-mcp-server -o jsonpath='{.items[0].metadata.name}')
echo "Using pod: $POD_NAME"

echo ""
echo "🧪 Testing health endpoint via pod port-forward..."
kubectl port-forward pod/$POD_NAME 8081:8080 -n python-mcp-server &
PORT_FORWARD_PID=$!

# Wait for port-forward to start
sleep 3

echo "Testing health endpoint..."
curl -s http://localhost:8081/health && echo "✅ Health check passed" || echo "❌ Health check failed"

echo ""
echo "Testing root endpoint..."
curl -s http://localhost:8081/ && echo "✅ Root endpoint passed" || echo "❌ Root endpoint failed"

echo ""
echo "Testing API health..."
curl -s http://localhost:8081/api/health && echo "✅ API health passed" || echo "❌ API health failed"

# Stop port-forward
echo ""
echo "🛑 Stopping port-forward..."
kill $PORT_FORWARD_PID 2>/dev/null
sleep 2

echo ""
echo "🔗 Testing with service port-forward (different port)..."
kubectl port-forward svc/python-mcp-server-service 8082:80 -n python-mcp-server &
SERVICE_PID=$!

# Wait for port-forward to start
sleep 3

echo "Testing service health endpoint..."
curl -s http://localhost:8082/health && echo "✅ Service health check passed" || echo "❌ Service health check failed"

echo ""
echo "Testing service root endpoint..."
curl -s http://localhost:8082/ && echo "✅ Service root endpoint passed" || echo "❌ Service root endpoint failed"

# Stop service port-forward
echo ""
echo "🛑 Stopping service port-forward..."
kill $SERVICE_PID 2>/dev/null
sleep 2

echo ""
echo "🔍 Testing with kubectl exec..."
echo "Testing health via kubectl exec..."
kubectl exec -n python-mcp-server $POD_NAME -- curl -s http://localhost:8080/health && echo "✅ Exec health check passed" || echo "❌ Exec health check failed"

echo ""
echo "Testing root via kubectl exec..."
kubectl exec -n python-mcp-server $POD_NAME -- curl -s http://localhost:8080/ | head -3 && echo "✅ Exec root check passed" || echo "❌ Exec root check failed"

echo ""
echo "🎉 Testing complete!"
echo ""
echo "📝 Service Information:"
echo "   Namespace: python-mcp-server"
echo "   Service: python-mcp-server-service"
echo "   Type: LoadBalancer"
echo "   Port: 80 -> 8080"
echo ""
echo "🔗 Access methods that work:"
echo "   1. Direct pod: kubectl port-forward pod/<pod-name> 8081:8080 -n python-mcp-server"
echo "   2. Service: kubectl port-forward svc/python-mcp-server-service 8082:80 -n python-mcp-server"
echo "   3. Exec: kubectl exec -n python-mcp-server <pod-name> -- curl http://localhost:8080/"