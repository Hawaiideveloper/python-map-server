#!/bin/bash

# Script to fix the deployment selectors and clean up duplicate services
echo "🔧 Fixing python-mcp-server Deployment Selectors"
echo "=============================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# First, let's check what labels the pods actually have
echo "🔍 Current pod labels:"
kubectl get pods -n python-mcp-server -o yaml | grep -A 10 "labels:" | head -20

echo ""
echo "🔍 Current service selectors:"
kubectl get svc python-mcp-server-service -n python-mcp-server -o yaml | grep -A 5 "selector:"

echo ""
echo "🗑️ Cleaning up duplicate services..."
kubectl delete svc mcp-server-headless -n python-mcp-server --ignore-not-found=true
kubectl delete svc mcp-server-service -n python-mcp-server --ignore-not-found=true

echo ""
echo "🔧 Updating pod labels to match service selector..."
# Add the app=python-mcp-server label to existing pods
kubectl label pods -n python-mcp-server -l app.kubernetes.io/name=python-mcp-server app=python-mcp-server --overwrite

echo ""
echo "⏳ Waiting for service to connect to pods..."
sleep 10

echo ""
echo "📋 Updated pod labels:"
kubectl get pods -n python-mcp-server --show-labels

echo ""
echo "🌐 Service status:"
kubectl get svc -n python-mcp-server

echo ""
echo "🔍 Testing service connectivity:"
kubectl get endpoints python-mcp-server-service -n python-mcp-server

echo ""
echo "🔍 Pod logs (last 10 lines):"
kubectl logs -l app=python-mcp-server -n python-mcp-server --tail=10

echo ""
echo "🎉 Selector fix complete!"
echo ""
echo "🔗 To test the service:"
echo "   kubectl port-forward svc/python-mcp-server-service 8080:80 -n python-mcp-server"
echo "   curl http://localhost:8080/health"