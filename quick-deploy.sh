#!/bin/bash

# Quick deployment script - run this in your working terminal
# This will deploy the test version first

echo "🚀 Quick Deploy - Python MCP Server to Kubernetes"
echo "================================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Create namespace and deploy
echo "📦 Creating namespace and deploying..."
kubectl create namespace mcp-server-test --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s-test-deployment.yaml -n mcp-server-test

echo "⏳ Waiting for deployment..."
kubectl rollout status deployment/python-mcp-server-test -n mcp-server-test --timeout=120s

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "📋 Pods:"
    kubectl get pods -n mcp-server-test
    echo ""
    echo "🌐 Services:"
    kubectl get svc -n mcp-server-test
    echo ""
    echo "🔍 Pod logs:"
    kubectl logs -l app=python-mcp-server -n mcp-server-test --tail=10
    echo ""
    echo "🔗 To test the service:"
    echo "   kubectl port-forward svc/python-mcp-server-test-service 8080:80 -n mcp-server-test"
    echo "   curl http://localhost:8080/health"
else
    echo "❌ Deployment failed. Check logs:"
    kubectl get events -n mcp-server-test --sort-by='.lastTimestamp'
fi