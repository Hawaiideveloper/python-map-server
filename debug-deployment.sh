#!/bin/bash

# Comprehensive debugging script for Python MCP Server deployment
echo "🔍 Comprehensive Deployment Debugging"
echo "===================================="

# Check Kubernetes connectivity
echo "🔍 Checking Kubernetes connectivity..."
if ! kubectl get nodes >/dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"
echo ""

# 1. Check deployment status
echo "📋 1. DEPLOYMENT STATUS"
echo "======================"
kubectl get deployment python-mcp-server -n python-mcp-server -o wide
echo ""

# 2. Check pod status
echo "📋 2. POD STATUS"
echo "==============="
kubectl get pods -n python-mcp-server -o wide
echo ""

# 3. Check service status
echo "📋 3. SERVICE STATUS"
echo "==================="
kubectl get svc -n python-mcp-server -o wide
echo ""

# 4. Check pod details
echo "📋 4. POD DETAILS"
echo "================"
kubectl describe pod -n python-mcp-server -l app=python-mcp-server
echo ""

# 5. Check container logs
echo "📋 5. CONTAINER LOGS"
echo "==================="
kubectl logs -n python-mcp-server -l app=python-mcp-server --tail=100
echo ""

# 6. Check recent events
echo "📋 6. RECENT EVENTS"
echo "=================="
kubectl get events -n python-mcp-server --sort-by='.lastTimestamp' | tail -20
echo ""

# 7. Check image pull secrets
echo "📋 7. IMAGE PULL SECRETS"
echo "======================="
kubectl get secret regcred -n python-mcp-server -o yaml | grep -A 5 "data:"
echo ""

# 8. Check if pods can access the image
echo "📋 8. IMAGE ACCESS TEST"
echo "======================"
kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].metadata.name}' | xargs -I {} kubectl exec -n python-mcp-server {} -- docker pull ghcr.io/hawaiideveloper/python-mcp-server:latest 2>&1 || echo "   Image pull test failed"
echo ""

# 9. Check container filesystem
echo "📋 9. CONTAINER FILESYSTEM"
echo "========================="
kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].metadata.name}' | xargs -I {} kubectl exec -n python-mcp-server {} -- ls -la /app/ 2>/dev/null || echo "   Cannot access container filesystem"
echo ""

# 10. Check Python modules
echo "📋 10. PYTHON MODULES"
echo "===================="
kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].metadata.name}' | xargs -I {} kubectl exec -n python-mcp-server {} -- ls -la /app/src/mcp_server/ 2>/dev/null || echo "   Cannot access Python modules"
echo ""

# 11. Check network connectivity
echo "📋 11. NETWORK CONNECTIVITY"
echo "=========================="
kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].metadata.name}' | xargs -I {} kubectl exec -n python-mcp-server {} -- netstat -tlnp 2>/dev/null || echo "   Cannot check network status"
echo ""

# 12. Check environment variables
echo "📋 12. ENVIRONMENT VARIABLES"
echo "==========================="
kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].metadata.name}' | xargs -I {} kubectl exec -n python-mcp-server {} -- env | grep -E "(ENVIRONMENT|HTTP_|PYTHON|LOG)" 2>/dev/null || echo "   Cannot access environment variables"
echo ""

# 13. Check resource usage
echo "📋 13. RESOURCE USAGE"
echo "===================="
kubectl top pods -n python-mcp-server 2>/dev/null || echo "   Metrics not available"
echo ""

# 14. Check image details
echo "📋 14. IMAGE DETAILS"
echo "==================="
kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].metadata.name}' | xargs -I {} kubectl exec -n python-mcp-server {} -- docker images | grep python-mcp-server 2>/dev/null || echo "   Cannot access Docker images"
echo ""

# 15. Check application startup
echo "📋 15. APPLICATION STARTUP TEST"
echo "==============================="
kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].metadata.name}' | xargs -I {} kubectl exec -n python-mcp-server {} -- python -c "import mcp_server; print('✅ MCP Server module imported successfully')" 2>/dev/null || echo "   ❌ MCP Server module import failed"
echo ""

echo "🎯 DEBUGGING COMPLETE!"
echo "====================="
echo "💡 Common issues to look for:"
echo "   - Image pull errors (should be fixed with AMD64 image)"
echo "   - Python import errors (module not found)"
echo "   - Port binding issues (app not listening on 33221)"
echo "   - Environment variable issues"
echo "   - Resource limits exceeded"
echo "   - Application startup errors"
echo ""
echo "🔧 Next steps:"
echo "   - Check the logs above for specific error messages"
echo "   - Look for 'Error' or 'Failed' in the output"
echo "   - Check if the application is binding to the correct port"