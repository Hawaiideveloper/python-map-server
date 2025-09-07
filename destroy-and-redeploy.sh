#!/bin/bash

# Script to completely destroy and redeploy with proper authentication
echo "🗑️ Destroying and Redeploying python-mcp-server"
echo "=============================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Use token from zshrc
if [ -z "$PYTHON_MCP_SERVER_GHCR_TOKEN" ]; then
    echo "❌ PYTHON_MCP_SERVER_GHCR_TOKEN not found in environment."
    echo "💡 Please source your zshrc file: source ~/.zshrc"
    exit 1
fi

export GITHUB_TOKEN="$PYTHON_MCP_SERVER_GHCR_TOKEN"

echo "🔍 Current deployment status:"
kubectl get pods -n python-mcp-server
kubectl get svc -n python-mcp-server

echo ""
echo "🗑️ Destroying existing deployment..."
kubectl delete deployment python-mcp-server -n python-mcp-server

echo ""
echo "🗑️ Destroying existing service..."
kubectl delete service python-mcp-server-service -n python-mcp-server

echo ""
echo "⏳ Waiting for cleanup..."
kubectl wait --for=delete pod -l app=python-mcp-server -n python-mcp-server --timeout=60s

echo ""
echo "🔐 Recreating GitHub Container Registry secret..."
kubectl delete secret regcred -n python-mcp-server --ignore-not-found=true
kubectl create secret docker-registry regcred \
    --docker-server=ghcr.io \
    --docker-username=hawaiideveloper \
    --docker-password="$GITHUB_TOKEN" \
    --docker-email=hawaiideveloper@users.noreply.github.com \
    --namespace=python-mcp-server

echo "✅ GitHub Container Registry secret recreated"

echo ""
echo "🚀 Deploying fresh with proper authentication..."

# Create the deployment file with imagePullSecrets
cat > k8s-production-deployment-fresh.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-mcp-server
  namespace: python-mcp-server
  labels:
    app: python-mcp-server
    version: "production"
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: python-mcp-server
  template:
    metadata:
      labels:
        app: python-mcp-server
        version: "production"
    spec:
      imagePullSecrets:
      - name: regcred
      containers:
      - name: python-mcp-server
        image: ghcr.io/hawaiideveloper/python-mcp-server:latest
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 33221
          protocol: TCP
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: HTTP_HOST
          value: "0.0.0.0"
        - name: HTTP_PORT
          value: "33221"
        - name: PYTHONPATH
          value: "/app/src"
        - name: LOG_LEVEL
          value: "info"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 33221
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 33221
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 2
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: logs
        emptyDir:
          sizeLimit: 1Gi
      - name: cache
        emptyDir:
          sizeLimit: 2Gi
      restartPolicy: Always
      terminationGracePeriodSeconds: 30

---
apiVersion: v1
kind: Service
metadata:
  name: python-mcp-server-service
  namespace: python-mcp-server
  labels:
    app: python-mcp-server
spec:
  type: LoadBalancer
  ports:
  - name: http
    port: 80
    targetPort: 33221
    protocol: TCP
  selector:
    app: python-mcp-server
EOF

echo "✅ Fresh deployment file created"

# Apply the fresh deployment
kubectl apply -f k8s-production-deployment-fresh.yaml

echo ""
echo "⏳ Waiting for fresh deployment to be ready..."
kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Fresh deployment successful!"
    echo ""
    echo "📋 Fresh deployment status:"
    kubectl get pods -n python-mcp-server
    echo ""
    echo "🌐 Service status:"
    kubectl get svc -n python-mcp-server
    echo ""
    echo "🔍 Service endpoints:"
    kubectl get endpoints python-mcp-server-service -n python-mcp-server
    echo ""
    echo "🧪 Testing fresh deployment..."
    
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
    echo "🎉 Fresh deployment successful!"
    echo ""
    echo "📝 Service Information:"
    echo "   Image: ghcr.io/hawaiideveloper/python-mcp-server:latest"
    echo "   Port: 80 -> 33221"
    echo "   Namespace: python-mcp-server"
    echo "   Authentication: GitHub Container Registry"
    
else
    echo "❌ Fresh deployment failed!"
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

# Clean up temporary file
rm -f k8s-production-deployment-fresh.yaml