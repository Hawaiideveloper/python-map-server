# Python MCP Server - Kubernetes Deployment

This directory contains production-ready Kubernetes manifests for deploying the Python MCP Server in a Kubernetes cluster.

## 📁 Directory Structure

```
k8s/
├── namespace.yaml       # Namespace and labels
├── configmap.yaml       # Configuration settings
├── secret.yaml          # Sensitive data (API keys, etc.)
├── rbac.yaml           # Service account and permissions
├── deployment.yaml      # Main application deployment
├── service.yaml        # Service and load balancer
├── ingress.yaml        # External access configuration
├── hpa.yaml            # Horizontal Pod Autoscaler & PDB
├── networkpolicy.yaml  # Network security policies
├── servicemonitor.yaml # Prometheus monitoring
├── deploy.sh           # Deployment automation script
├── manage.sh           # Management operations script
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Deploy to Kubernetes

```bash
# Make scripts executable
chmod +x deploy.sh manage.sh

# Deploy everything
./deploy.sh
```

### 2. Access the Server

```bash
# Port forward for local access
./manage.sh forward

# Test the deployment
./manage.sh test
```

## ✅ Deployment Checklist

Use this checklist to validate the repository before deploying to a kubeadm Kubernetes cluster. Unit tests under `tests/test_k8s_deployment_checklist.py` will verify each item and mark the box below when the test passes.

- [x] Manifests present (namespace, configmap, secret, rbac, deployment, service, ingress, hpa, networkpolicy, servicemonitor)
- [x] Deployment scripts executable (`deploy.sh`, `manage.sh`)
- [x] Deployment has liveness/readiness probes
- [x] HPA configured (min/max replicas present)
- [x] NetworkPolicy present and restrictive rules defined
- [x] ServiceMonitor present for Prometheus scraping

- [x] External access configured (LoadBalancer or Ingress with TLS)
- [x] Internal cluster access (ClusterIP/headless service and correct port) for pod-to-pod communication
- [x] n8n integration guidance present (example workflow or notes)
- [x] Developer access instructions (VS Code, Cursor, Codespaces) for remote development


## 🛠️ Management Commands

The `manage.sh` script provides common operations:

```bash
./manage.sh status      # Show deployment status
./manage.sh logs        # View application logs
./manage.sh logs -f     # Follow logs in real-time
./manage.sh shell       # Get shell access to pod
./manage.sh scale 5     # Scale to 5 replicas
./manage.sh restart     # Restart the deployment
./manage.sh forward     # Port forward on 3011
./manage.sh test        # Test deployment health
./manage.sh events      # Show namespace events
./manage.sh describe    # Describe resources
./manage.sh top         # Show resource usage
./manage.sh delete      # Delete entire deployment
```

## 📋 Deployment Features

### Security
- **RBAC**: Minimal required permissions
- **Security Context**: Non-root container execution
- **Network Policies**: Restricted network access
- **Read-only Root Filesystem**: Enhanced security
- **Pod Security Standards**: Compliant with restricted profile

### High Availability
- **2+ Replicas**: Multi-pod deployment
- **Pod Anti-Affinity**: Spread across nodes
- **Pod Disruption Budget**: Maintain availability during updates
- **Rolling Updates**: Zero-downtime deployments
- **Health Checks**: Liveness, readiness, and startup probes

### Scalability
- **Horizontal Pod Autoscaler**: Auto-scale 2-10 pods
- **Resource Limits**: Proper CPU/memory constraints
- **Load Balancer**: Distribute traffic across pods
- **Headless Service**: Direct pod access for clustering

### Monitoring
- **Prometheus Metrics**: Built-in metrics endpoint
- **ServiceMonitor**: Automatic Prometheus discovery
- **Structured Logging**: JSON logs with correlation IDs
- **Health Endpoints**: Multiple health check endpoints

### Networking
- **LoadBalancer Service**: External access
- **Ingress**: HTTP/HTTPS routing with TLS support
- **Network Policies**: Micro-segmentation
- **Service Mesh Ready**: Compatible with Istio/Linkerd

## 🔧 Configuration

### Environment Variables (ConfigMap)
- `ENVIRONMENT`: Production mode settings
- `PORT`: Application port (default: 3011)
- `LOG_LEVEL`: Logging verbosity
- `ENABLE_AUTH`: Authentication toggle
- `CORS_ENABLED`: CORS configuration

### Secrets
- `API_KEY`: Authentication API key
- `JWT_SECRET`: JWT signing secret
- `DB_PASSWORD`: Database password (if needed)

## 🏗️ Platform Engineering Features

### GitOps Ready
- Declarative manifests
- Environment separation
- Version controlled configuration
- Automated deployment pipelines

### Cloud Native
- 12-factor app compliance
- Stateless design
- External configuration
- Health check endpoints

### Observability
- Structured logging
- Metrics collection
- Distributed tracing ready
- Error tracking integration

## 🔍 Troubleshooting

### Common Issues

1. **Pod Not Starting**
```bash
./manage.sh describe
./manage.sh events
./manage.sh logs
```

2. **Health Checks Failing**
```bash
# Check health endpoint directly
kubectl exec -it deployment/python-mcp-server -n mcp-server -- curl localhost:3011/health
```

3. **Network Issues**
```bash
# Check service endpoints
kubectl get endpoints -n mcp-server

# Test internal connectivity
kubectl exec -it deployment/python-mcp-server -n mcp-server -- nslookup mcp-server-service
```

4. **Resource Issues**
```bash
./manage.sh top
kubectl describe node <node-name>
```

### Scaling Issues

```bash
# Check HPA status
kubectl get hpa -n mcp-server

# Manual scaling
./manage.sh scale 3

# Check pod distribution
kubectl get pods -n mcp-server -o wide
```

## 🔒 Security Considerations

### RBAC
The deployment uses minimal RBAC permissions:
- Read-only access to core Kubernetes resources
- No write permissions to cluster resources
- Namespace-scoped service account

### Network Security
- Network policies restrict ingress/egress
- Only necessary ports exposed
- Internal communication encrypted (with service mesh)

### Container Security
- Non-root user execution
- Read-only root filesystem
- No privileged escalation
- Minimal base image

## 🌐 Production Deployment

### Prerequisites
- Kubernetes 1.24+
- NGINX Ingress Controller (for Ingress)
- Prometheus Operator (for ServiceMonitor)
- Metrics Server (for HPA)
- cert-manager (for TLS certificates)

### Production Checklist
- [ ] Update `secret.yaml` with real secrets
- [ ] Configure proper domain in `ingress.yaml`
- [ ] Set up TLS certificates
- [ ] Configure monitoring alerts
- [ ] Set resource limits based on load testing
- [ ] Configure backup strategy
- [ ] Set up log aggregation
- [ ] Configure network policies for your environment

### Environment-Specific Deployments

```bash
# Development
export NAMESPACE=mcp-server-dev
export IMAGE_TAG=dev
./deploy.sh

# Staging
export NAMESPACE=mcp-server-staging
export IMAGE_TAG=staging
./deploy.sh

# Production
export NAMESPACE=mcp-server-prod
export IMAGE_TAG=v1.0.0
./deploy.sh
```

## 📊 Monitoring & Alerting

### Metrics Available
- HTTP request metrics
- Response time percentiles
- Error rates
- System resource usage
- Custom business metrics

### Prometheus Queries
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Response time P99
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

## 🤝 Contributing

When modifying the Kubernetes manifests:

1. Follow Kubernetes best practices
2. Update resource limits based on testing
3. Maintain security policies
4. Test with different cluster configurations
5. Update documentation

## 📚 References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Platform Engineering Best Practices](https://github.com/Hawaiideveloper/mcp-kubernetes-platform-engineer)
- [Security Hardening Guide](https://github.com/AlbrightLaboratories/arc)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
