#!/bin/bash

# Script to monitor the deployment progress
echo "📊 Monitoring python-mcp-server Deployment"
echo "========================================"

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

echo "📋 Current deployment status:"
kubectl get pods -n python-mcp-server

echo ""
echo "🔍 Deployment rollout status:"
kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=60s

echo ""
echo "📊 Pod details:"
kubectl get pods -n python-mcp-server -o wide

echo ""
echo "🔍 Service status:"
kubectl get svc -n python-mcp-server

echo ""
echo "🔍 Service endpoints:"
kubectl get endpoints python-mcp-server-service -n python-mcp-server

echo ""
echo "🔍 Recent events:"
kubectl get events -n python-mcp-server --sort-by='.lastTimestamp' | tail -10

echo ""
echo "🔍 Pod logs (if any pods are running):"
kubectl get pods -n python-mcp-server -l app=python-mcp-server --field-selector=status.phase=Running -o name | head -1 | xargs -I {} kubectl logs {} -n python-mcp-server --tail=10 2>/dev/null || echo "No running pods yet"

echo ""
echo "🧪 Testing deployment (if ready)..."

# Check if any pods are ready
READY_PODS=$(kubectl get pods -n python-mcp-server -l app=python-mcp-server --field-selector=status.phase=Running --no-headers | wc -l)

if [ "$READY_PODS" -gt 0 ]; then
    echo "✅ Found $READY_PODS running pod(s), testing..."
    
    # Get first running pod
    POD_NAME=$(kubectl get pods -n python-mcp-server -l app=python-mcp-server --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')
    echo "Using pod: $POD_NAME"
    
    echo ""
    echo "Testing port 33221 via kubectl exec..."
    kubectl exec -n python-mcp-server $POD_NAME -- curl -s http://localhost:33221/health && echo "✅ Health check on port 33221 passed" || echo "❌ Health check on port 33221 failed"
    
    echo ""
    echo "Testing root endpoint on port 33221..."
    kubectl exec -n python-mcp-server $POD_NAME -- curl -s http://localhost:33221/ | head -3 && echo "✅ Root endpoint on port 33221 passed" || echo "❌ Root endpoint on port 33221 failed"
    
    echo ""
    echo "🔗 Testing service port-forward..."
    kubectl port-forward svc/python-mcp-server-service 8080:80 -n python-mcp-server &
    PORT_FORWARD_PID=$!
    
    # Wait for port-forward to start
    sleep 3
    
    echo "Testing service via port-forward..."
    curl -s http://localhost:8080/health && echo "✅ Service health check passed" || echo "❌ Service health check failed"
    
    echo ""
    echo "Testing service root endpoint..."
    curl -s http://localhost:8080/ | head -3 && echo "✅ Service root endpoint passed" || echo "❌ Service root endpoint failed"
    
    # Stop port-forward
    kill $PORT_FORWARD_PID 2>/dev/null
    
    echo ""
    echo "🎉 Deployment testing complete!"
else
    echo "⏳ No running pods yet, deployment still in progress..."
    echo "💡 Run this script again in a few moments to check status"
fi

echo ""
echo "📝 Current Status Summary:"
echo "   Namespace: python-mcp-server"
echo "   Image: ghcr.io/hawaiideveloper/python-mcp-server:latest"
echo "   Port: 80 -> 33221"
echo "   Authentication: GitHub Container Registry secret created"
echo "   Ready Pods: $READY_PODS"