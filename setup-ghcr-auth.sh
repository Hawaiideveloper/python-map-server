#!/bin/bash

# Script to set up GitHub Container Registry authentication for Kubernetes
echo "🔐 Setting up GitHub Container Registry Authentication"
echo "===================================================="

# Check if we can connect to Kubernetes
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "💡 Make sure you're in your working terminal that can connect to K8s."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Check if GitHub token is available
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN environment variable not found."
    echo "💡 Please set your GitHub token:"
    echo "   export GITHUB_TOKEN=your_github_token_here"
    echo "   or add it to your ~/.zshrc file"
    exit 1
fi

echo "✅ GitHub token found"

# Create namespace if it doesn't exist
echo "📦 Ensuring namespace exists..."
kubectl create namespace python-mcp-server --dry-run=client -o yaml | kubectl apply -f -

# Create GitHub Container Registry secret
echo "🔐 Creating GitHub Container Registry secret..."
kubectl create secret docker-registry regcred \
    --docker-server=ghcr.io \
    --docker-username=hawaiideveloper \
    --docker-password=$GITHUB_TOKEN \
    --docker-email=hawaiideveloper@users.noreply.github.com \
    --namespace=python-mcp-server \
    --dry-run=client -o yaml | kubectl apply -f -

echo "✅ GitHub Container Registry secret created"

# Update deployment to use the secret
echo "🔧 Updating deployment to use image pull secret..."

# Create a temporary deployment file with imagePullSecrets
cat > k8s-production-deployment-with-secret.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-mcp-server
  namespace: python-mcp-server
  labels:
    app: python-mcp-server
    version: "production"
  annotations:
    deployment.kubernetes.io/revision: "1"
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

---
apiVersion: v1
kind: Namespace
metadata:
  name: python-mcp-server
  labels:
    name: python-mcp-server
EOF

echo "✅ Deployment file with image pull secret created"

# Apply the deployment
echo "🚀 Deploying with GitHub Container Registry authentication..."
kubectl apply -f k8s-production-deployment-with-secret.yaml

echo ""
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Deployment with GitHub Container Registry authentication successful!"
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
    echo "🎉 GitHub Container Registry authentication setup successful!"
    echo ""
    echo "📝 Service Information:"
    echo "   Image: ghcr.io/hawaiideveloper/python-mcp-server:latest"
    echo "   Port: 80 -> 33221"
    echo "   Namespace: python-mcp-server"
    echo "   Authentication: GitHub Container Registry"
    
else
    echo "❌ Deployment with GitHub Container Registry authentication failed!"
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
rm -f k8s-production-deployment-with-secret.yaml