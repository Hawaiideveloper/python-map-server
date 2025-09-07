#!/bin/bash

# Script to debug what's running in the pods
echo "🔍 Debugging python-mcp-server Pods"
echo "================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Get pod name
POD_NAME=$(kubectl get pods -n python-mcp-server -l app=python-mcp-server -o jsonpath='{.items[0].metadata.name}')
echo "Using pod: $POD_NAME"

echo ""
echo "🔍 Pod details:"
kubectl describe pod $POD_NAME -n python-mcp-server | grep -A 10 -B 5 "Port:"

echo ""
echo "🔍 Container ports:"
kubectl get pod $POD_NAME -n python-mcp-server -o jsonpath='{.spec.containers[0].ports}' | jq .

echo ""
echo "🔍 Process list in pod:"
kubectl exec -n python-mcp-server $POD_NAME -- ps aux

echo ""
echo "🔍 Network connections in pod:"
kubectl exec -n python-mcp-server $POD_NAME -- netstat -tlnp

echo ""
echo "🔍 Environment variables:"
kubectl exec -n python-mcp-server $POD_NAME -- env | grep -E "(PORT|HOST|ENVIRONMENT)"

echo ""
echo "🔍 Testing localhost connectivity in pod:"
kubectl exec -n python-mcp-server $POD_NAME -- curl -v http://localhost:8080/ 2>&1 | head -10

echo ""
echo "🔍 Pod logs (last 20 lines):"
kubectl logs $POD_NAME -n python-mcp-server --tail=20