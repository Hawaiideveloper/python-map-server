#!/bin/bash

# Script to deploy with port 33221
echo "🚀 Deploying python-mcp-server with Port 33221"
echo "============================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Check current deployment
echo "🔍 Current deployment status:"
kubectl get pods -n python-mcp-server
kubectl get svc -n python-mcp-server

echo ""
echo "🔄 Updating deployment with port 33221..."

# Apply the updated configuration
kubectl apply -f k8s-production-deployment.yaml

echo ""
echo "⏳ Waiting for rolling update to complete..."
kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Deployment update successful!"
    echo ""
    echo "📋 Updated deployment status:"
    kubectl get pods -n python-mcp-server
    echo ""
    echo "🌐 Updated service status:"
    kubectl get svc -n python-mcp-server
    echo ""
    echo "🔍 Service endpoints:"
    kubectl get endpoints python-mcp-server-service -n python-mcp-server
    echo ""
    echo "🧪 Testing new port configuration..."
    
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
    
    # Stop port-forward
    kill $PORT_FORWARD_PID 2>/dev/null
    
    echo ""
    echo "🎉 Port 33221 deployment successful!"
    echo ""
    echo "📝 Service Information:"
    echo "   Namespace: python-mcp-server"
    echo "   Service: python-mcp-server-service"
    echo "   Type: LoadBalancer"
    echo "   Port: 80 -> 33221"
    echo ""
    echo "🔗 Access methods:"
    echo "   1. Service: kubectl port-forward svc/python-mcp-server-service 8080:80 -n python-mcp-server"
    echo "   2. Direct pod: kubectl port-forward pod/<pod-name> 8081:33221 -n python-mcp-server"
    echo "   3. Exec: kubectl exec -n python-mcp-server <pod-name> -- curl http://localhost:33221/"
    
else
    echo "❌ Deployment update failed!"
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