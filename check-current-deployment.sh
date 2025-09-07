#!/bin/bash

# Script to check the current python-mcp-server deployment before replacing it
echo "🔍 Checking Current python-mcp-server Deployment"
echo "=============================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"
echo ""

# Find all python-mcp-server deployments
echo "📋 All python-mcp-server deployments:"
kubectl get deployments --all-namespaces | grep python-mcp-server

echo ""
echo "📋 Detailed deployment information:"
kubectl get deployments --all-namespaces -o wide | grep python-mcp-server

echo ""
echo "📋 Associated services:"
kubectl get services --all-namespaces | grep python-mcp-server

echo ""
echo "📋 Pods:"
kubectl get pods --all-namespaces | grep python-mcp-server

echo ""
echo "📋 Current image being used:"
kubectl get deployments --all-namespaces -o jsonpath='{range .items[?(@.metadata.name=="python-mcp-server")]}{.metadata.namespace}{"\t"}{.spec.template.spec.containers[0].image}{"\n"}{end}'

echo ""
echo "📋 Current replicas:"
kubectl get deployments --all-namespaces -o jsonpath='{range .items[?(@.metadata.name=="python-mcp-server")]}{.metadata.namespace}{"\t"}{.spec.replicas}{"\n"}{end}'

echo ""
echo "🔍 Recent events:"
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | grep python-mcp-server | tail -5