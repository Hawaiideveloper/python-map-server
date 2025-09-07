#!/bin/bash

# Script to check existing deployments before deploying new ones
echo "🔍 Checking existing Python MCP deployments..."
echo "=============================================="

echo "📋 All deployments with 'python' in the name:"
kubectl get deployments --all-namespaces | grep python

echo ""
echo "📋 All services with 'python' or 'mcp' in the name:"
kubectl get services --all-namespaces | grep -E "(python|mcp)"

echo ""
echo "📋 All namespaces:"
kubectl get namespaces

echo ""
echo "🔍 Specific checks:"
echo "Default namespace deployments:"
kubectl get deployments -n default 2>/dev/null || echo "No deployments in default namespace"

echo ""
echo "MCP-server namespace deployments:"
kubectl get deployments -n mcp-server 2>/dev/null || echo "No mcp-server namespace or deployments"

echo ""
echo "Python-mcp namespace deployments:"
kubectl get deployments -n python-mcp 2>/dev/null || echo "No python-mcp namespace or deployments"