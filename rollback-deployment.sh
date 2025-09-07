#!/bin/bash

# Script to rollback the python-mcp-server deployment if needed
echo "🔄 Rollback python-mcp-server Deployment"
echo "======================================"

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Check current deployment status
echo "🔍 Current deployment status:"
kubectl get pods -n python-mcp-server -l app=python-mcp-server

echo ""
echo "📋 Deployment history:"
kubectl rollout history deployment/python-mcp-server -n python-mcp-server

echo ""
echo "🔄 Rolling back to previous version..."
kubectl rollout undo deployment/python-mcp-server -n python-mcp-server

echo ""
echo "⏳ Waiting for rollback to complete..."
kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=120s

if [ $? -eq 0 ]; then
    echo "✅ Rollback successful!"
    echo ""
    echo "📋 Rolled back pods:"
    kubectl get pods -n python-mcp-server -l app=python-mcp-server
    echo ""
    echo "🔍 Pod logs (last 10 lines):"
    kubectl logs -l app=python-mcp-server -n python-mcp-server --tail=10
else
    echo "❌ Rollback failed!"
    echo "🔍 Checking events:"
    kubectl get events -n python-mcp-server --sort-by='.lastTimestamp' | tail -10
fi