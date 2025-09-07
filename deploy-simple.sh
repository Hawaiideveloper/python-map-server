#!/bin/bash

# Simple deployment script for Python MCP Server to Kubernetes
# This script will deploy the test version first, then the production version

echo "🚀 Deploying Python MCP Server to Kubernetes..."

# Check if kubectl can connect to cluster
echo "📡 Checking Kubernetes cluster connectivity..."
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig and network connectivity."
    echo "💡 Make sure you're connected to the right network and your kubeconfig is correct."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Create namespace if it doesn't exist
echo "📦 Creating namespace if needed..."
kubectl create namespace mcp-server-test --dry-run=client -o yaml | kubectl apply -f -

# Deploy the test version first
echo "🔧 Deploying test version..."
kubectl apply -f k8s-test-deployment.yaml -n mcp-server-test

echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/python-mcp-server-test -n mcp-server-test --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Test deployment 'python-mcp-server-test' is ready."
    
    echo "📋 Checking pods status:"
    kubectl get pods -l app=python-mcp-server -n mcp-server-test
    
    echo "🌐 Checking service status:"
    kubectl get svc python-mcp-server-test-service -n mcp-server-test
    
    echo "🔍 Getting pod logs (last 20 lines):"
    kubectl logs -l app=python-mcp-server -n mcp-server-test --tail=20
    
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Test the service: kubectl port-forward svc/python-mcp-server-test-service 8080:80 -n mcp-server-test"
    echo "2. Access the service at: http://localhost:8080"
    echo "3. Check health endpoint: http://localhost:8080/health"
    echo ""
    echo "🔄 To deploy production version, run:"
    echo "   kubectl apply -f k8s/deployment.yaml -n mcp-server"
    
else
    echo "❌ Test deployment failed to become ready."
    echo "🔍 Checking events for troubleshooting:"
    kubectl get events -n mcp-server-test --field-selector involvedObject.name=python-mcp-server-test --sort-by='.lastTimestamp'
    exit 1
fi