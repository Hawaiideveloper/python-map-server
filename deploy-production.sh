#!/bin/bash

# Production deployment script for Python MCP Server to Kubernetes
# This script deploys the production version with LoadBalancer service

echo "🚀 Deploying Python MCP Server to Kubernetes (Production)..."

# Check if kubectl can connect to cluster
echo "📡 Checking Kubernetes cluster connectivity..."
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig and network connectivity."
    echo "💡 Make sure you're connected to the right network and your kubeconfig is correct."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f k8s-production-deployment.yaml

# Wait for namespace to be ready
kubectl wait --for=condition=Ready namespace/mcp-server --timeout=60s

# Deploy the production version
echo "🔧 Deploying production version..."
kubectl apply -f k8s-production-deployment.yaml

echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/python-mcp-server -n mcp-server --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Production deployment 'python-mcp-server' is ready."
    
    echo "📋 Checking pods status:"
    kubectl get pods -l app=python-mcp-server -n mcp-server
    
    echo "🌐 Checking service status:"
    kubectl get svc python-mcp-server-service -n mcp-server
    
    echo "🔍 Getting pod logs (last 20 lines):"
    kubectl logs -l app=python-mcp-server -n mcp-server --tail=20
    
    echo ""
    echo "🎉 Production deployment successful!"
    echo ""
    echo "📝 Service information:"
    kubectl get svc python-mcp-server-service -n mcp-server -o wide
    
    echo ""
    echo "🔗 To access the service:"
    echo "1. If LoadBalancer has external IP: Use the EXTERNAL-IP from above"
    echo "2. For local testing: kubectl port-forward svc/python-mcp-server-service 8080:80 -n mcp-server"
    echo "3. Health check: curl http://localhost:8080/health"
    
else
    echo "❌ Production deployment failed to become ready."
    echo "🔍 Checking events for troubleshooting:"
    kubectl get events -n mcp-server --field-selector involvedObject.name=python-mcp-server --sort-by='.lastTimestamp'
    exit 1
fi