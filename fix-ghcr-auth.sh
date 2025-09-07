#!/bin/bash

# Script to fix GitHub Container Registry authentication
echo "🔧 Fixing GitHub Container Registry Authentication"
echo "==============================================="

# Use token from zshrc
if [ -z "$PYTHON_MCP_SERVER_GHCR_TOKEN" ]; then
    echo "❌ PYTHON_MCP_SERVER_GHCR_TOKEN not found in environment."
    echo "💡 Please source your zshrc file: source ~/.zshrc"
    exit 1
fi

export GITHUB_TOKEN="$PYTHON_MCP_SERVER_GHCR_TOKEN"

echo "🔍 Diagnosing GitHub token permissions..."

# Test token with GitHub API
echo "Testing GitHub API access..."
USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
echo "User: $(echo $USER_INFO | jq -r '.login')"
echo "Token scopes: $(echo $USER_INFO | jq -r '.permissions // "No permissions info"')"

# Check if the repository exists and is accessible
echo ""
echo "🔍 Checking repository access..."
REPO_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/hawaiideveloper/python-mcp-server)
if echo "$REPO_INFO" | jq -e '.name' > /dev/null 2>&1; then
    echo "✅ Repository accessible: $(echo $REPO_INFO | jq -r '.name')"
    echo "Repository visibility: $(echo $REPO_INFO | jq -r '.visibility // "unknown"')"
else
    echo "❌ Repository not accessible or doesn't exist"
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
    echo "❌ No packages found or no access"
fi

echo ""
echo "🔧 Trying alternative authentication methods..."

# Method 1: Try with different username format
echo "Method 1: Trying with different username format..."
kubectl delete secret regcred -n python-mcp-server --ignore-not-found=true
kubectl create secret docker-registry regcred \
    --docker-server=ghcr.io \
    --docker-username=hawaiideveloper \
    --docker-password="$GITHUB_TOKEN" \
    --docker-email=hawaiideveloper@users.noreply.github.com \
    --namespace=python-mcp-server

# Method 2: Try with token as username
echo "Method 2: Trying with token as username..."
kubectl delete secret regcred-token -n python-mcp-server --ignore-not-found=true
kubectl create secret docker-registry regcred-token \
    --docker-server=ghcr.io \
    --docker-username="$GITHUB_TOKEN" \
    --docker-password="$GITHUB_TOKEN" \
    --docker-email=hawaiideveloper@users.noreply.github.com \
    --namespace=python-mcp-server

echo ""
echo "🔧 Creating deployment with multiple authentication methods..."

# Create deployment with both secrets
cat > k8s-production-deployment-multi-auth.yaml << EOF
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
      - name: regcred-token
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

echo "✅ Multi-auth deployment file created"

# Apply the deployment
kubectl apply -f k8s-production-deployment-multi-auth.yaml

echo ""
echo "⏳ Waiting for deployment with multiple auth methods..."
kubectl rollout status deployment/python-mcp-server -n python-mcp-server --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Deployment with multiple auth methods successful!"
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
    echo "🎉 Multi-auth deployment successful!"
    
else
    echo "❌ Multi-auth deployment failed!"
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
    echo "💡 If still failing, the token may need different permissions:"
    echo "   1. Go to GitHub Settings > Developer settings > Personal access tokens"
    echo "   2. Edit your token and ensure it has 'packages:read' permission"
    echo "   3. Or try using a different token with proper GHCR permissions"
fi

# Clean up temporary file
rm -f k8s-production-deployment-multi-auth.yaml