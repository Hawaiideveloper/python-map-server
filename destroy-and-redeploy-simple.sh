#!/bin/bash

# Simple destroy and re-deploy script
echo "🗑️  Destroying and Re-deploying Python MCP Server"
echo "==============================================="

# Check Kubernetes connectivity
echo "🔍 Checking Kubernetes connectivity..."
if ! kubectl get nodes >/dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "💡 Please run this from a terminal that can connect to Kubernetes"
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Destroy existing resources
echo "🗑️  Destroying existing resources..."
kubectl delete deployment python-mcp-server -n python-mcp-server --ignore-not-found=true
kubectl delete service python-mcp-server-service -n python-mcp-server --ignore-not-found=true

echo "⏳ Waiting for cleanup..."
sleep 10

# Deploy new version
echo "🚀 Deploying new version..."
kubectl apply -f k8s-production-deployment.yaml

echo "⏳ Waiting for deployment to start..."
sleep 15

# Check status
echo "🔍 Checking deployment status..."
kubectl get pods -n python-mcp-server
kubectl get svc -n python-mcp-server

echo ""
echo "🎯 Deployment complete!"
echo "💡 Monitor with: kubectl get pods -n python-mcp-server -w"