#!/bin/bash

# Script to test a new GitHub token and fix the deployment
echo "🧪 Testing New GitHub Token and Fixing Deployment"
echo "==============================================="

# Check if PYTHON_MCP_SERVER_GHCR_TOKEN is set
if [ -z "$PYTHON_MCP_SERVER_GHCR_TOKEN" ]; then
    echo "❌ PYTHON_MCP_SERVER_GHCR_TOKEN environment variable not set."
    echo "💡 Please source your zshrc file:"
    echo "   source ~/.zshrc"
    echo "   then run this script again"
    exit 1
fi

# Use the token from zshrc
export GITHUB_TOKEN="$PYTHON_MCP_SERVER_GHCR_TOKEN"
echo "✅ Testing token from zshrc: ${GITHUB_TOKEN:0:10}..."

# Test token with GitHub API
echo "🔍 Testing GitHub API access..."
USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
USER_LOGIN=$(echo $USER_INFO | jq -r '.login // "null"')

if [ "$USER_LOGIN" != "null" ] && [ "$USER_LOGIN" != "" ]; then
    echo "✅ GitHub API authentication successful!"
    echo "User: $USER_LOGIN"
    
    # Check token scopes
    TOKEN_SCOPES=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | jq -r '.permissions // "No permissions info"')
    echo "Token scopes: $TOKEN_SCOPES"
    
    # Check repository access
    echo ""
    echo "🔍 Checking repository access..."
    REPO_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/hawaiideveloper/python-mcp-server)
    if echo "$REPO_INFO" | jq -e '.name' > /dev/null 2>&1; then
        echo "✅ Repository accessible: $(echo $REPO_INFO | jq -r '.name')"
        echo "Repository visibility: $(echo $REPO_INFO | jq -r '.visibility // "unknown"')"
    else
        echo "❌ Repository not accessible"
        echo "Response: $REPO_INFO"
    fi
    
    # Check GitHub Container Registry packages
    echo ""
    echo "🔍 Checking GitHub Container Registry packages..."
    PACKAGES=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user/packages?package_type=container)
    if echo "$PACKAGES" | jq -e '.[0].name' > /dev/null 2>&1; then
        echo "✅ Found packages:"
        echo "$PACKAGES" | jq -r '.[].name'
    else
        echo "⚠️  No packages found or no access (this might be normal)"
    fi
    
    echo ""
    echo "🔧 Updating Kubernetes with new token..."
    
    # Delete old secrets
    kubectl delete secret regcred -n python-mcp-server --ignore-not-found=true
    kubectl delete secret regcred-token -n python-mcp-server --ignore-not-found=true
    
    # Create new secret with the working token
    kubectl create secret docker-registry regcred \
        --docker-server=ghcr.io \
        --docker-username=hawaiideveloper \
        --docker-password="$GITHUB_TOKEN" \
        --docker-email=hawaiideveloper@users.noreply.github.com \
        --namespace=python-mcp-server
    
    echo "✅ New GitHub Container Registry secret created"
    
    echo ""
    echo "🚀 Restarting deployment with new token..."
    
    # Restart the deployment to use the new secret
    kubectl rollout restart deployment/python-mcp-server -n python-mcp-server
    
    echo ""
    echo "⏳ Waiting for deployment to restart..."
    kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=300s
    
    if [ $? -eq 0 ]; then
        echo "✅ Deployment restart successful!"
        echo ""
        echo "📋 Deployment status:"
        kubectl get pods -n python-mcp-server
        echo ""
        echo "🌐 Service status:"
        kubectl get svc -n python-mcp-server
        echo ""
        echo "🔍 Service endpoints:"
        kubectl get endpoints python-mcp-server-service -n python-mcp-server
        echo ""
        echo "🧪 Testing deployment..."
        
        # Get pod name
        POD_NAME=$(kubectl get pods -n python-mcp-server -l app=python-mcp-server -o jsonpath='{.items[0].metadata.name}')
        echo "Using pod: $POD_NAME"
        
        echo ""
        echo "Testing port 33221 via kubectl exec..."
        kubectl exec -n python-mcp-server $POD_NAME -- curl -s http://localhost:33221/health && echo "✅ Health check on port 33221 passed" || echo "❌ Health check on port 33221 failed"
        
        echo ""
        echo "Testing root endpoint on port 33221..."
        kubectl exec -n python-mcp-server $POD_NAME -- curl -s http://localhost:33221/ | head -3 && echo "✅ Root endpoint on port 33221 passed" || echo "❌ Root endpoint on port 33221 failed"
        
        echo ""
        echo "🔗 Testing service port-forward..."
        kubectl port-forward svc/python-mcp-server-service 8080:80 -n python-mcp-server &
        PORT_FORWARD_PID=$!
        
        # Wait for port-forward to start
        sleep 3
        
        echo "Testing service via port-forward..."
        curl -s http://localhost:8080/health && echo "✅ Service health check passed" || echo "❌ Service health check failed"
        
        echo ""
        echo "Testing service root endpoint..."
        curl -s http://localhost:8080/ | head -3 && echo "✅ Service root endpoint passed" || echo "❌ Service root endpoint failed"
        
        # Stop port-forward
        kill $PORT_FORWARD_PID 2>/dev/null
        
        echo ""
        echo "🎉 New token authentication successful!"
        echo ""
        echo "📝 Service Information:"
        echo "   Image: ghcr.io/hawaiideveloper/python-mcp-server:latest"
        echo "   Port: 80 -> 33221"
        echo "   Namespace: python-mcp-server"
        echo "   Authentication: New GitHub token"
        
    else
        echo "❌ Deployment restart failed!"
        echo ""
        echo "🔍 Checking events for troubleshooting:"
        kubectl get events -n python-mcp-server --sort-by='.lastTimestamp' | tail -10
        echo ""
        echo "🔍 Checking pod status:"
        kubectl get pods -n python-mcp-server -l app=python-mcp-server
        echo ""
        echo "🔍 Checking pod logs:"
        kubectl logs -l app=python-mcp-server -n python-mcp-server --tail=20
    fi
    
else
    echo "❌ GitHub API authentication failed!"
    echo "Response: $USER_INFO"
    echo ""
    echo "💡 Please check your token:"
    echo "   1. Make sure it's copied correctly"
    echo "   2. Ensure it has the right permissions"
    echo "   3. Check if it's expired"
    echo "   4. Try creating a new token"
fi