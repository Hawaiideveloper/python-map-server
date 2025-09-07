#!/bin/bash

# Deployment script that handles existing python-mcp-server deployment
# This will replace the existing deployment with our new production-ready version

echo "🚀 Deploying Python MCP Server (Replacing Existing)"
echo "=================================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Check existing deployments
echo "🔍 Checking existing deployments..."
kubectl get deployments --all-namespaces | grep python-mcp-server

echo ""
echo "📋 Current python-mcp-server deployments:"
kubectl get deployments --all-namespaces -o wide | grep python-mcp-server

# Create namespace
echo ""
echo "📦 Creating/updating namespace..."
kubectl create namespace mcp-server --dry-run=client -o yaml | kubectl apply -f -

# Deploy with rolling update
echo ""
echo "🔄 Deploying with rolling update (will replace existing)..."
kubectl apply -f k8s-production-deployment.yaml

echo ""
echo "⏳ Waiting for rolling update to complete..."
kubectl rollout status deployment/python-mcp-server -n mcp-server --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "📋 Updated pods:"
    kubectl get pods -n mcp-server -l app=python-mcp-server
    echo ""
    echo "🌐 Updated services:"
    kubectl get svc -n mcp-server -l app=python-mcp-server
    echo ""
    echo "🔍 Pod logs (last 10 lines):"
    kubectl logs -l app=python-mcp-server -n mcp-server --tail=10
    echo ""
    echo "🎉 Successfully replaced python-mcp-server deployment!"
    echo ""
    echo "🔗 Service information:"
    kubectl get svc python-mcp-server-service -n mcp-server -o wide
    echo ""
    echo "📝 To test the service:"
    echo "   kubectl port-forward svc/python-mcp-server-service 8080:80 -n mcp-server"
    echo "   curl http://localhost:8080/health"
else
    echo "❌ Deployment failed. Checking events..."
    kubectl get events -n mcp-server --sort-by='.lastTimestamp' | tail -10
    echo ""
    echo "🔍 Checking pod status:"
    kubectl get pods -n mcp-server -l app=python-mcp-server
    echo ""
    echo "🔍 Checking pod logs:"
    kubectl logs -l app=python-mcp-server -n mcp-server --tail=20
fi