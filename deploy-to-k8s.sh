#!/bin/bash

# Python MCP Server Kubernetes Deployment Script
# This script helps deploy and test the new Python MCP Server

set -e

echo "🚀 Python MCP Server Kubernetes Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check cluster connectivity
echo "🔍 Checking Kubernetes cluster connectivity..."
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    echo "Please ensure your cluster is running and kubectl is configured correctly"
    exit 1
fi
print_status "Connected to Kubernetes cluster"

# Check for existing python-mcp deployment
echo "🔍 Checking for existing python-mcp deployment..."
if kubectl get deployment python-mcp &> /dev/null; then
    print_warning "Found existing python-mcp deployment"
    echo "Current deployment status:"
    kubectl get deployment python-mcp -o wide
    echo ""
    read -p "Do you want to replace the existing deployment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing python-mcp deployment..."
        kubectl delete deployment python-mcp --ignore-not-found=true
        kubectl delete service python-mcp --ignore-not-found=true
        print_status "Existing deployment removed"
    else
        echo "Using test deployment name instead..."
        DEPLOYMENT_FILE="k8s-test-deployment.yaml"
    fi
else
    print_status "No existing python-mcp deployment found"
    DEPLOYMENT_FILE="k8s-deployment.yaml"
fi

# Deploy the new Python MCP Server
echo "🚀 Deploying Python MCP Server..."
kubectl apply -f ${DEPLOYMENT_FILE:-k8s-deployment.yaml}

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/python-mcp-server${DEPLOYMENT_FILE:+-test} --timeout=300s

# Get service information
echo "📡 Service information:"
kubectl get svc -l app=python-mcp-server

# Get pod information
echo "🔄 Pod information:"
kubectl get pods -l app=python-mcp-server

# Test the deployment
echo "🧪 Testing the deployment..."
POD_NAME=$(kubectl get pods -l app=python-mcp-server -o jsonpath='{.items[0].metadata.name}')
if [ -n "$POD_NAME" ]; then
    echo "Testing health endpoint..."
    kubectl exec $POD_NAME -- curl -s http://localhost:8080/health || print_warning "Health check failed - pod may still be starting"
    
    echo "Verifying documentation is included..."
    DOC_COUNT=$(kubectl exec $POD_NAME -- find /app/docs -name "*.html" | wc -l)
    if [ "$DOC_COUNT" -gt 1000 ]; then
        print_status "Documentation verified: $DOC_COUNT HTML files found"
    else
        print_warning "Documentation count seems low: $DOC_COUNT files"
    fi
else
    print_error "No pods found for python-mcp-server"
fi

echo ""
echo "🎉 Deployment complete!"
echo "======================"
echo "To access the service:"
echo "  kubectl port-forward svc/python-mcp-server${DEPLOYMENT_FILE:+-test}-service 8080:80"
echo ""
echo "Then visit: http://localhost:8080"
echo "Health check: http://localhost:8080/health"
echo "API docs: http://localhost:8080/docs"