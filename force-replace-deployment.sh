#!/bin/bash

# Script to force replace the python-mcp-server deployment
# This will delete the old deployment and create a new one

echo "🔄 Force Replacing python-mcp-server Deployment"
echo "============================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Check current deployments
echo "🔍 Checking current python-mcp-server deployments..."
kubectl get deployments --all-namespaces | grep python-mcp-server

echo ""
echo "📋 Current deployment details:"
kubectl get deployments --all-namespaces -o wide | grep python-mcp-server

# Create namespace
echo ""
echo "📦 Ensuring namespace exists..."
kubectl create namespace python-mcp-server --dry-run=client -o yaml | kubectl apply -f -

# Delete existing deployment if it exists
echo ""
echo "🗑️ Deleting existing python-mcp-server deployment..."
kubectl delete deployment python-mcp-server --ignore-not-found=true

# Wait a moment for cleanup
echo "⏳ Waiting for cleanup..."
sleep 5

# Deploy the new version
echo ""
echo "🚀 Deploying new production-ready version..."
echo "   Image: hawaiideveloper/python-mcp-server:latest"
echo "   Replicas: 3"
echo "   Strategy: RollingUpdate (zero downtime)"

kubectl apply -f k8s-production-deployment.yaml

echo ""
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Deployment replacement successful!"
    echo ""
    echo "📋 New deployment status:"
    kubectl get pods -n python-mcp-server
    echo ""
    echo "🌐 Service status:"
    kubectl get svc -n python-mcp-server
    echo ""
    echo "🔍 Pod logs (last 10 lines):"
    kubectl logs -l app=python-mcp-server -n python-mcp-server --tail=10
    echo ""
    echo "🎉 Successfully replaced python-mcp-server!"
    echo ""
    echo "📝 Service information:"
    kubectl get svc python-mcp-server-service -n python-mcp-server -o wide
    echo ""
    echo "🔗 To test the new deployment:"
    echo "   kubectl port-forward svc/python-mcp-server-service 8080:80 -n python-mcp-server"
    echo "   curl http://localhost:8080/health"
    echo ""
    echo "📊 Deployment details:"
    kubectl describe deployment python-mcp-server -n python-mcp-server | grep -A 10 "Image:"
else
    echo "❌ Deployment replacement failed!"
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