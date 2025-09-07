#!/bin/bash

# Script to fix the deployment from a working Kubernetes terminal
echo "🔧 Fixing Deployment from Working Kubernetes Terminal"
echo "=================================================="

# Check if PYTHON_MCP_SERVER_GHCR_TOKEN is set
if [ -z "$PYTHON_MCP_SERVER_GHCR_TOKEN" ]; then
    echo "❌ PYTHON_MCP_SERVER_GHCR_TOKEN not found in environment."
    echo "💡 Please source your zshrc file: source ~/.zshrc"
    exit 1
fi

export GITHUB_TOKEN="$PYTHON_MCP_SERVER_GHCR_TOKEN"
echo "✅ Using token: ${GITHUB_TOKEN:0:10}..."

# Test GitHub API
echo "🔍 Testing GitHub API access..."
USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
USER_LOGIN=$(echo $USER_INFO | jq -r '.login // "null"')

if [ "$USER_LOGIN" != "null" ] && [ "$USER_LOGIN" != "" ]; then
    echo "✅ GitHub API authentication successful!"
    echo "User: $USER_LOGIN"
else
    echo "❌ GitHub API authentication failed!"
    exit 1
fi

# Check Kubernetes connectivity
echo "🔍 Checking Kubernetes connectivity..."
if ! kubectl get nodes >/dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "💡 Please run this from a terminal that can connect to Kubernetes"
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Create or update the GitHub Container Registry secret
echo "🔧 Creating/updating GitHub Container Registry secret..."
kubectl create secret docker-registry regcred \
    --docker-server=ghcr.io \
    --docker-username=hawaiideveloper \
    --docker-password="$GITHUB_TOKEN" \
    --docker-email=hawaiideveloper@users.noreply.github.com \
    --namespace=python-mcp-server \
    --dry-run=client -o yaml | kubectl apply -f -

echo "✅ GitHub Container Registry secret updated"

# Restart the deployment to use the new secret
echo "🚀 Restarting deployment with new token..."
kubectl rollout restart deployment/python-mcp-server -n python-mcp-server

echo "⏳ Waiting for deployment to restart..."
kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=300s

# Check the deployment status
echo "🔍 Checking deployment status..."
kubectl get pods -n python-mcp-server

# Check if pods are running
POD_STATUS=$(kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
if [ "$POD_STATUS" = "Running" ]; then
    echo "✅ Deployment is running successfully!"
    
    # Get the service info
    echo "🔍 Service information:"
    kubectl get svc -n python-mcp-server
    
    # Test the service
    echo "🧪 Testing service connectivity..."
    kubectl port-forward -n python-mcp-server svc/python-mcp-server 33221:33221 &
    PORT_FORWARD_PID=$!
    
    sleep 5
    
    if curl -s http://localhost:33221/health >/dev/null 2>&1; then
        echo "✅ Service is responding on port 33221!"
        echo "🎉 Deployment is working correctly!"
    else
        echo "⚠️  Service not responding on port 33221"
        echo "💡 Check pod logs: kubectl logs -n python-mcp-server deployment/python-mcp-server"
    fi
    
    # Clean up port forward
    kill $PORT_FORWARD_PID 2>/dev/null
else
    echo "❌ Deployment is not running properly"
    echo "🔍 Pod status: $POD_STATUS"
    echo "💡 Check pod logs: kubectl logs -n python-mcp-server deployment/python-mcp-server"
fi

echo ""
echo "🎯 Next steps:"
echo "1. If deployment is working, you can connect to it from Cursor"
echo "2. If there are issues, check the pod logs"
echo "3. The service should be available on port 33221"