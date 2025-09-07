#!/bin/bash

# Check container logs to see what's happening
echo "🔍 Checking Container Logs"
echo "========================="

NAMESPACE="python-mcp-server"

# Check pod status
echo "📋 Pod Status:"
kubectl get pods -n $NAMESPACE

echo ""
echo "📋 Container Logs (last 50 lines):"
kubectl logs -n $NAMESPACE -l app=python-mcp-server --tail=50

echo ""
echo "📋 Recent Events:"
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10

echo ""
echo "📋 Pod Details:"
kubectl describe pod -n $NAMESPACE -l app=python-mcp-server | grep -A 10 -B 5 "Readiness\|Liveness\|Port"