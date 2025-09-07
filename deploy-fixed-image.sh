#!/bin/bash

# Deploy the fixed Python MCP Server image
echo "🚀 Deploying Fixed Python MCP Server Image"
echo "=========================================="

NAMESPACE="python-mcp-server"
DEPLOYMENT_NAME="python-mcp-server"

# Check Kubernetes connectivity
echo "🔍 Checking Kubernetes connectivity..."
if ! kubectl get nodes >/dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi
echo "✅ Connected to Kubernetes cluster"

# Force restart the deployment to pull the new image
echo "🔄 Restarting deployment to pull new image..."
kubectl rollout restart deployment/$DEPLOYMENT_NAME -n $NAMESPACE

# Wait for rollout to complete
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=300s

# Check pod status
echo "🔍 Checking pod status..."
kubectl get pods -n $NAMESPACE

# Check if pods are running
echo "🔍 Checking if pods are running..."
kubectl get pods -n $NAMESPACE -o jsonpath='{.items[*].status.phase}' | grep -q "Running"

if [ $? -eq 0 ]; then
    echo "✅ Pods are running successfully!"
    echo ""
    echo "🎯 Deployment Status:"
    kubectl get deployment $DEPLOYMENT_NAME -n $NAMESPACE
    echo ""
    echo "🎯 Service Status:"
    kubectl get svc -n $NAMESPACE
    echo ""
    echo "🎯 Pod Status:"
    kubectl get pods -n $NAMESPACE
else
    echo "❌ Pods are not running. Checking logs..."
    kubectl logs -n $NAMESPACE -l app=python-mcp-server --tail=20
fi

echo ""
echo "🎉 Deployment complete!"