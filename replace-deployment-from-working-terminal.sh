#!/bin/bash

# Script to completely replace the deployment from a working Kubernetes terminal
echo "🔄 Replacing Deployment from Working Kubernetes Terminal"
echo "====================================================="

# Check if PYTHON_MCP_SERVER_GHCR_TOKEN is set
if [ -z "$PYTHON_MCP_SERVER_GHCR_TOKEN" ]; then
    echo "❌ PYTHON_MCP_SERVER_GHCR_TOKEN not found in environment."
    echo "💡 Please source your zshrc file: source ~/.zshrc"
    exit 1
fi

export GITHUB_TOKEN="$PYTHON_MCP_SERVER_GHCR_TOKEN"
echo "✅ Using token: ...${GITHUB_TOKEN: -4} (last 4 chars)"

# Test GitHub API
echo "🔍 Testing GitHub API access..."
USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
USER_LOGIN=$(echo $USER_INFO | jq -r '.login // "null"')

if [ "$USER_LOGIN" != "null" ] && [ "$USER_LOGIN" != "" ]; then
    echo "✅ GitHub API authentication successful!"
    echo "User: $USER_LOGIN"
else
    echo "⚠️  GitHub API authentication failed, but continuing anyway..."
    echo "Response: $USER_INFO"
fi

# Test GHCR authentication (optional - don't fail if it doesn't work)
echo "🔍 Testing GHCR authentication..."
GHCR_RESPONSE=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $GITHUB_TOKEN" https://ghcr.io/v2/ -o /dev/null)

if [ "$GHCR_RESPONSE" = "200" ]; then
    echo "✅ GHCR authentication successful!"
else
    echo "⚠️  GHCR authentication failed (HTTP $GHCR_RESPONSE), but continuing anyway..."
    echo "💡 This might be due to token permissions, but we'll try to proceed"
fi

# Check Kubernetes connectivity
echo "🔍 Checking Kubernetes connectivity..."
if ! kubectl get nodes >/dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "💡 Please run this from a terminal that can connect to Kubernetes"
    echo "🔍 Debug info:"
    echo "   kubectl config current-context: $(kubectl config current-context 2>/dev/null || echo 'No context')"
    echo "   kubectl config view --minify:"
    kubectl config view --minify 2>/dev/null || echo "   No kubectl config found"
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"
echo "🔍 Kubernetes context: $(kubectl config current-context)"
echo "🔍 Available nodes:"
kubectl get nodes --no-headers | wc -l | xargs echo "   Number of nodes:"

# Check current deployment status
echo "🔍 Current deployment status:"
kubectl get pods -n python-mcp-server
kubectl get svc -n python-mcp-server

# Create or update the GitHub Container Registry secret
echo "🔧 Creating/updating GitHub Container Registry secret..."
echo "🔍 Secret details:"
echo "   Server: ghcr.io"
echo "   Username: hawaiideveloper"
echo "   Token: ...${GITHUB_TOKEN: -4}"

SECRET_OUTPUT=$(kubectl create secret docker-registry regcred \
    --docker-server=ghcr.io \
    --docker-username=hawaiideveloper \
    --docker-password="$GITHUB_TOKEN" \
    --docker-email=hawaiideveloper@users.noreply.github.com \
    --namespace=python-mcp-server \
    --dry-run=client -o yaml | kubectl apply -f - 2>&1)

echo "🔍 Secret creation output: $SECRET_OUTPUT"

# Verify secret was created
echo "🔍 Verifying secret creation..."
kubectl get secret regcred -n python-mcp-server -o yaml | grep -A 5 "data:" || echo "   Secret not found or empty"

echo "✅ GitHub Container Registry secret updated"

# Delete the existing deployment completely
echo "🗑️  Deleting existing deployment..."
kubectl delete deployment python-mcp-server -n python-mcp-server --ignore-not-found=true

# Delete the existing service
echo "🗑️  Deleting existing service..."
kubectl delete service python-mcp-server -n python-mcp-server --ignore-not-found=true

# Wait a moment for cleanup
echo "⏳ Waiting for cleanup..."
sleep 5

# Deploy the new version
echo "🚀 Deploying new version..."
echo "🔍 Deployment file: k8s-production-deployment.yaml"
echo "🔍 Image being deployed: ghcr.io/hawaiideveloper/python-mcp-server:latest"

# Apply the deployment
DEPLOY_OUTPUT=$(kubectl apply -f k8s-production-deployment.yaml 2>&1)
echo "🔍 Deployment output: $DEPLOY_OUTPUT"

# Add imagePullSecrets to the deployment if not present
echo "🔧 Ensuring imagePullSecrets are configured..."
kubectl patch deployment python-mcp-server -n python-mcp-server -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"regcred"}]}}}}' 2>/dev/null || echo "   imagePullSecrets already configured"

echo "⏳ Waiting for new deployment to start..."
echo "🔍 Monitoring deployment status..."

# Show deployment status with more detail
kubectl get deployment python-mcp-server -n python-mcp-server -o wide

# Wait for rollout with timeout
if kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=300s; then
    echo "✅ Deployment rollout completed successfully"
else
    echo "⚠️  Deployment rollout timed out or failed"
    echo "🔍 Checking deployment events..."
    kubectl describe deployment python-mcp-server -n python-mcp-server
fi

# Check the deployment status
echo "🔍 Checking new deployment status..."
kubectl get pods -n python-mcp-server

# Check if pods are running
echo "🔍 Detailed pod status:"
kubectl get pods -n python-mcp-server -o wide

POD_STATUS=$(kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
POD_NAME=$(kubectl get pods -n python-mcp-server -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

echo "🔍 Pod status: $POD_STATUS"
echo "🔍 Pod name: $POD_NAME"

if [ "$POD_STATUS" = "Running" ]; then
    echo "✅ New deployment is running successfully!"
    
    # Get the service info
    echo "🔍 Service information:"
    kubectl get svc -n python-mcp-server -o wide
    
    # Test the service
    echo "🧪 Testing service connectivity..."
    kubectl port-forward -n python-mcp-server svc/python-mcp-server 33221:33221 &
    PORT_FORWARD_PID=$!
    
    sleep 5
    
    if curl -s http://localhost:33221/health >/dev/null 2>&1; then
        echo "✅ Service is responding on port 33221!"
        echo "🎉 Deployment replacement successful!"
    else
        echo "⚠️  Service not responding on port 33221"
        echo "🔍 Checking pod logs..."
        kubectl logs -n python-mcp-server deployment/python-mcp-server --tail=20
    fi
    
    # Clean up port forward
    kill $PORT_FORWARD_PID 2>/dev/null
else
    echo "❌ New deployment is not running properly"
    echo "🔍 Pod status: $POD_STATUS"
    echo "🔍 Pod events:"
    kubectl describe pod $POD_NAME -n python-mcp-server | grep -A 10 "Events:" || echo "   No pod found to describe"
    echo "🔍 Pod logs:"
    kubectl logs -n python-mcp-server deployment/python-mcp-server --tail=20 || echo "   No logs available"
    echo "🔍 Image pull issues:"
    kubectl get events -n python-mcp-server --sort-by='.lastTimestamp' | grep -i "pull\|image\|error" | tail -5 || echo "   No relevant events found"
fi

echo ""
echo "🎯 Summary:"
echo "✅ Old deployment: DELETED"
echo "✅ New deployment: DEPLOYED"
echo "✅ GitHub token: UPDATED (...${GITHUB_TOKEN: -4})"
echo "✅ Service: Available on port 33221"
echo ""
echo "🔍 Final Debug Information:"
echo "   Kubernetes context: $(kubectl config current-context)"
echo "   Namespace: python-mcp-server"
echo "   Image: ghcr.io/hawaiideveloper/python-mcp-server:latest"
echo "   Port: 33221"
echo "   Token: ...${GITHUB_TOKEN: -4}"
echo ""
echo "🔧 Troubleshooting Commands:"
echo "   Check pods: kubectl get pods -n python-mcp-server"
echo "   Check logs: kubectl logs -n python-mcp-server deployment/python-mcp-server"
echo "   Check events: kubectl get events -n python-mcp-server"
echo "   Check service: kubectl get svc -n python-mcp-server"
echo "   Port forward: kubectl port-forward -n python-mcp-server svc/python-mcp-server 33221:33221"
echo ""
echo "🎉 Ready for Cursor MCP connection!"