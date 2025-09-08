# 🚀 Kubernetes Deployment Examples

## Quick Deployment

### 1. **Create Namespace**
```bash
kubectl apply -f examples/kubernetes/namespace.example.yaml
```

### 2. **Deploy the MCP Server**
```bash
# Update the image URL in deployment.example.yaml first
kubectl apply -f examples/kubernetes/deployment.example.yaml
```

### 3. **Create Service**
```bash
kubectl apply -f examples/kubernetes/service.example.yaml
```

### 4. **Get Access Information**
```bash
# For LoadBalancer
kubectl get service python-mcp-server-service -n python-mcp-server

# For NodePort
kubectl get service python-mcp-server-service -n python-mcp-server -o wide
```

## Configuration Notes

### **Before Deploying:**
1. Replace `YOUR_USERNAME` in `deployment.example.yaml` with your GitHub username
2. Build and push your Docker image:
   ```bash
   docker build -t ghcr.io/YOUR_USERNAME/python-mcp-server:latest .
   docker push ghcr.io/YOUR_USERNAME/python-mcp-server:latest
   ```

### **Service Types:**
- **LoadBalancer**: Best for cloud environments (AWS, GCP, Azure)
- **NodePort**: Good for local clusters (minikube, kind)
- **ClusterIP**: Internal cluster access only

### **Access Your Server:**
- Health check: `http://YOUR_IP:YOUR_PORT/health`
- API docs: `http://YOUR_IP:YOUR_PORT/docs`
- WebSocket MCP: `ws://YOUR_IP:YOUR_PORT/mcp`

## Scaling
```bash
# Scale to 3 replicas
kubectl scale deployment python-mcp-server --replicas=3 -n python-mcp-server
```

## Monitoring
```bash
# Check pods
kubectl get pods -n python-mcp-server

# View logs
kubectl logs -f deployment/python-mcp-server -n python-mcp-server
```
