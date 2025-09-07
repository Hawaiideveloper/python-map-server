#!/bin/bash

# Script to replace the existing python-mcp-server deployment
# This will perform a rolling update to replace the old deployment

echo "🔄 Replacing python-mcp-server Deployment"
echo "========================================"

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Check current deployment
echo "🔍 Checking current python-mcp-server deployment..."
kubectl get deployments --all-namespaces | grep python-mcp-server

echo ""
echo "📋 Current deployment details:"
kubectl get deployments --all-namespaces -o wide | grep python-mcp-server

# Create namespace if it doesn't exist
echo ""
echo "📦 Ensuring namespace exists..."
kubectl create namespace python-mcp-server --dry-run=client -o yaml | kubectl apply -f -

# Deploy the new version (this will replace the existing one)
echo ""
echo "🚀 Deploying new production-ready version..."
echo "   Image: hawaiideveloper/python-mcp-server:latest"
echo "   Replicas: 3"
echo "   Strategy: RollingUpdate (zero downtime)"

kubectl apply -f k8s-production-deployment.yaml

echo ""
echo "⏳ Waiting for rolling update to complete..."
kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Deployment replacement successful!"
    echo ""
    echo "📋 New deployment status:"
    kubectl get pods -n python-mcp-server -l app=python-mcp-server
    echo ""
    echo "🌐 Service status:"
    kubectl get svc -n python-mcp-server -l app=python-mcp-server
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
    echo ""
    echo "💡 If deployment failed, you can rollback with:"
    echo "   kubectl rollout undo deployment/python-mcp-server -n python-mcp-server"
fi