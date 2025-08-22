#!/bin/bash
set -e

# Python MCP Server Kubernetes Deployment Script
# Based on platform engineering best practices

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="python-mcp-server"
APP_NAME="python-mcp-server"
IMAGE_TAG="latest"
DEPLOYMENT_TIMEOUT="300s"
# Allow skipping local Docker build (useful when Docker daemon isn't available)
SKIP_LOCAL_BUILD="${SKIP_LOCAL_BUILD:-false}"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$SCRIPT_DIR/../k8s"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

header() {
    echo
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE} $1${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
}

# Check prerequisites
check_prerequisites() {
    header "🔍 Checking Prerequisites"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed or not in PATH"
        exit 1
    fi
    # Some kubectl versions don't support --short; be tolerant
    KUBECTL_CLIENT_VER=$(kubectl version --client 2>/dev/null || true)
    success "kubectl found: ${KUBECTL_CLIENT_VER}"
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    success "Connected to cluster: $(kubectl config current-context)"
    
    # Check Docker image exists (optional)
    if [ "$SKIP_LOCAL_BUILD" = "true" ]; then
        log "SKIP_LOCAL_BUILD=true, skipping local Docker image build/check"
    else
        if command -v docker &> /dev/null; then
            if docker info &> /dev/null; then
                if ! docker image inspect $APP_NAME:$IMAGE_TAG &> /dev/null; then
                    warning "Docker image $APP_NAME:$IMAGE_TAG not found locally"
                    log "Building Docker image..."
                    cd "$SCRIPT_DIR/../../"
                    docker build -t $APP_NAME:$IMAGE_TAG .
                    success "Docker image built successfully"
                else
                    success "Docker image $APP_NAME:$IMAGE_TAG found"
                fi
            else
                warning "Docker daemon not available; skipping local image build"
            fi
        else
            warning "Docker not installed; skipping local image build"
        fi
    fi
    
    # Check if running in Docker Desktop or kind (local clusters)
    CONTEXT=$(kubectl config current-context)
    if [[ "$CONTEXT" == *"docker-desktop"* ]] || [[ "$CONTEXT" == *"kind"* ]]; then
        log "Detected local cluster: $CONTEXT"
        log "Loading Docker image into cluster..."
        if [[ "$CONTEXT" == *"kind"* ]]; then
            kind load docker-image $APP_NAME:$IMAGE_TAG
        fi
        success "Image loaded into local cluster"
    fi
}

# Deploy to Kubernetes
deploy_kubernetes() {
    header "🚀 Deploying to Kubernetes"
    
    # Apply manifests in order
    log "Creating namespace..."
    kubectl apply -f "$K8S_DIR/namespace.yaml"
    
    log "Creating RBAC resources..."
    kubectl apply -f "$K8S_DIR/rbac.yaml"
    
    log "Creating ConfigMap..."
    kubectl apply -f "$K8S_DIR/configmap.yaml"
    
    log "Creating Secret..."
    kubectl apply -f "$K8S_DIR/secret.yaml"
    
    log "Creating Services..."
    kubectl apply -f "$K8S_DIR/service.yaml"
    
    log "Creating NetworkPolicy..."
    if kubectl get crd networkpolicies.networking.k8s.io &> /dev/null; then
        kubectl apply -f "$K8S_DIR/networkpolicy.yaml"
        success "NetworkPolicy applied"
    else
        warning "NetworkPolicy CRD not found, skipping network policy"
    fi
    
    log "Creating Deployment..."
    kubectl apply -f "$K8S_DIR/deployment.yaml"
    
    log "Creating HPA and PDB..."
    kubectl apply -f "$K8S_DIR/hpa.yaml"
    
    log "Creating Ingress..."
    kubectl apply -f "$K8S_DIR/ingress.yaml"
    
    log "Creating ServiceMonitor..."
    if kubectl get crd servicemonitors.monitoring.coreos.com &> /dev/null; then
        kubectl apply -f "$K8S_DIR/servicemonitor.yaml"
        success "ServiceMonitor applied"
    else
        warning "ServiceMonitor CRD not found, skipping Prometheus monitoring"
    fi
    
    success "All manifests applied successfully"
}

# Wait for deployment
wait_for_deployment() {
    header "⏳ Waiting for Deployment"
    
    log "Waiting for pods to be ready..."
    kubectl wait --namespace=$NAMESPACE \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/name=$APP_NAME \
        --timeout=$DEPLOYMENT_TIMEOUT
    
    success "Deployment is ready!"
}

# Get deployment status
get_status() {
    header "📊 Deployment Status"
    
    log "Namespace resources:"
    kubectl get all -n $NAMESPACE
    
    echo
    log "Pod details:"
    kubectl get pods -n $NAMESPACE -o wide
    
    echo
    log "Service endpoints:"
    kubectl get svc -n $NAMESPACE
    
    echo
    log "Ingress status:"
    kubectl get ingress -n $NAMESPACE
    
    echo
    log "HPA status:"
    kubectl get hpa -n $NAMESPACE
}

# Test deployment
test_deployment() {
    header "🧪 Testing Deployment"
    
    # Get service details
    SERVICE_TYPE=$(kubectl get svc mcp-server-service -n $NAMESPACE -o jsonpath='{.spec.type}')
    
    if [[ "$SERVICE_TYPE" == "LoadBalancer" ]]; then
        log "Waiting for LoadBalancer IP..."
        kubectl wait --namespace=$NAMESPACE \
            --for=jsonpath='{.status.loadBalancer.ingress}' \
            service/mcp-server-service \
            --timeout=60s || true
            
        EXTERNAL_IP=$(kubectl get svc mcp-server-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [[ -z "$EXTERNAL_IP" ]]; then
            EXTERNAL_IP=$(kubectl get svc mcp-server-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
        fi
        
        if [[ -n "$EXTERNAL_IP" ]]; then
            log "Testing LoadBalancer endpoint: http://$EXTERNAL_IP:3011"
            if curl -f "http://$EXTERNAL_IP:3011/health" &> /dev/null; then
                success "LoadBalancer health check passed!"
                echo "🌐 External URL: http://$EXTERNAL_IP:3011"
            else
                warning "LoadBalancer health check failed or still starting"
            fi
        else
            warning "LoadBalancer IP not yet assigned"
        fi
    fi
    
    # Test via port-forward
    log "Testing via port-forward..."
    kubectl port-forward -n $NAMESPACE svc/mcp-server-service 3011:3011 &
    PORT_FORWARD_PID=$!
    
    sleep 5
    
    if curl -f "http://localhost:3011/health" &> /dev/null; then
        success "Port-forward health check passed!"
        echo "🔗 Local URL: http://localhost:3011"
        echo "📊 Admin Dashboard: http://localhost:3011/admin"
        echo "📡 WebSocket MCP: ws://localhost:3011/mcp"
    else
        warning "Port-forward health check failed"
    fi
    
    # Clean up port-forward
    kill $PORT_FORWARD_PID &> /dev/null || true
}

# Show helpful commands
show_commands() {
    header "🎛️  Useful Commands"
    
    echo -e "${CYAN}# View logs${NC}"
    echo "kubectl logs -f deployment/$APP_NAME -n $NAMESPACE"
    echo
    echo -e "${CYAN}# Scale deployment${NC}"
    echo "kubectl scale deployment/$APP_NAME --replicas=3 -n $NAMESPACE"
    echo
    echo -e "${CYAN}# Port forward for local testing${NC}"
    echo "kubectl port-forward svc/mcp-server-service 3011:3011 -n $NAMESPACE"
    echo
    echo -e "${CYAN}# Get pod shell${NC}"
    echo "kubectl exec -it deployment/$APP_NAME -n $NAMESPACE -- /bin/bash"
    echo
    echo -e "${CYAN}# View events${NC}"
    echo "kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
    echo
    echo -e "${CYAN}# Delete deployment${NC}"
    echo "kubectl delete namespace $NAMESPACE"
    echo
    echo -e "${CYAN}# Monitor HPA${NC}"
    echo "kubectl get hpa -n $NAMESPACE -w"
}

# Main deployment flow
main() {
    header "🐳 Python MCP Server - Kubernetes Deployment"
    echo "  Namespace: $NAMESPACE"
    echo "  Image: $APP_NAME:$IMAGE_TAG"
    echo "  Context: $(kubectl config current-context)"
    echo
    
    check_prerequisites
    deploy_kubernetes
    wait_for_deployment
    get_status
    test_deployment
    show_commands
    
    success "🎉 Deployment completed successfully!"
    echo
    echo -e "${GREEN}Your Python MCP Server is now running in Kubernetes!${NC}"
    echo -e "${CYAN}Access it locally with:${NC} kubectl port-forward svc/mcp-server-service 3011:3011 -n $NAMESPACE"
}

# Run with error handling
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    trap 'error "Deployment failed at line $LINENO"' ERR
    main "$@"
fi
