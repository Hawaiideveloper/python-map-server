#!/bin/bash
set -e

# Kubernetes Management Script for Python MCP Server
# Provides common operations for the deployed MCP server

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

NAMESPACE="mcp-server"
APP_NAME="python-mcp-server"

log() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  status    - Show deployment status"
    echo "  logs      - View application logs"
    echo "  shell     - Get shell access to pod"
    echo "  scale     - Scale the deployment"
    echo "  restart   - Restart the deployment"
    echo "  forward   - Port forward for local access"
    echo "  test      - Test the deployment health"
    echo "  delete    - Delete the deployment"
    echo "  events    - Show namespace events"
    echo "  describe  - Describe deployment resources"
    echo "  top       - Show resource usage"
    echo
}

check_deployment() {
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        error "Namespace $NAMESPACE not found. Run deploy.sh first."
        exit 1
    fi
}

cmd_status() {
    check_deployment
    echo -e "${PURPLE}📊 Deployment Status${NC}"
    echo
    
    echo -e "${CYAN}Pods:${NC}"
    kubectl get pods -n $NAMESPACE -o wide
    echo
    
    echo -e "${CYAN}Services:${NC}"
    kubectl get svc -n $NAMESPACE
    echo
    
    echo -e "${CYAN}Ingress:${NC}"
    kubectl get ingress -n $NAMESPACE
    echo
    
    echo -e "${CYAN}HPA:${NC}"
    kubectl get hpa -n $NAMESPACE
    echo
    
    echo -e "${CYAN}Deployment:${NC}"
    kubectl get deployment -n $NAMESPACE
}

cmd_logs() {
    check_deployment
    echo -e "${PURPLE}📋 Application Logs${NC}"
    
    if [[ "$2" == "-f" ]] || [[ "$2" == "--follow" ]]; then
        kubectl logs -f deployment/$APP_NAME -n $NAMESPACE
    else
        kubectl logs deployment/$APP_NAME -n $NAMESPACE --tail=100
    fi
}

cmd_shell() {
    check_deployment
    echo -e "${PURPLE}🐚 Getting shell access...${NC}"
    kubectl exec -it deployment/$APP_NAME -n $NAMESPACE -- /bin/bash
}

cmd_scale() {
    check_deployment
    local replicas=${2:-3}
    echo -e "${PURPLE}📈 Scaling to $replicas replicas...${NC}"
    kubectl scale deployment/$APP_NAME --replicas=$replicas -n $NAMESPACE
    kubectl rollout status deployment/$APP_NAME -n $NAMESPACE
    success "Scaled to $replicas replicas"
}

cmd_restart() {
    check_deployment
    echo -e "${PURPLE}🔄 Restarting deployment...${NC}"
    kubectl rollout restart deployment/$APP_NAME -n $NAMESPACE
    kubectl rollout status deployment/$APP_NAME -n $NAMESPACE
    success "Deployment restarted"
}

cmd_forward() {
    check_deployment
    local port=${2:-3011}
    echo -e "${PURPLE}🔗 Port forwarding on port $port...${NC}"
    echo "Access the server at: http://localhost:$port"
    echo "Press Ctrl+C to stop port forwarding"
    kubectl port-forward svc/mcp-server-service $port:3011 -n $NAMESPACE
}

cmd_test() {
    check_deployment
    echo -e "${PURPLE}🧪 Testing deployment...${NC}"
    
    # Port forward in background
    kubectl port-forward svc/mcp-server-service 3011:3011 -n $NAMESPACE &
    local pf_pid=$!
    
    sleep 3
    
    echo "Testing health endpoint..."
    if curl -f http://localhost:3011/health &> /dev/null; then
        success "Health check passed!"
        
        echo "Testing root endpoint..."
        if curl -s http://localhost:3011/ | jq . &> /dev/null; then
            success "API endpoint accessible!"
        else
            warning "API endpoint test failed"
        fi
    else
        error "Health check failed"
    fi
    
    # Clean up port forward
    kill $pf_pid &> /dev/null || true
}

cmd_delete() {
    check_deployment
    echo -e "${RED}🗑️  Deleting deployment...${NC}"
    read -p "Are you sure you want to delete the entire deployment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace $NAMESPACE
        success "Deployment deleted"
    else
        log "Deletion cancelled"
    fi
}

cmd_events() {
    check_deployment
    echo -e "${PURPLE}📅 Namespace Events${NC}"
    kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'
}

cmd_describe() {
    check_deployment
    echo -e "${PURPLE}📄 Resource Descriptions${NC}"
    
    echo -e "${CYAN}Deployment:${NC}"
    kubectl describe deployment $APP_NAME -n $NAMESPACE
    echo
    
    echo -e "${CYAN}Pods:${NC}"
    kubectl describe pods -l app.kubernetes.io/name=$APP_NAME -n $NAMESPACE
    echo
    
    echo -e "${CYAN}Service:${NC}"
    kubectl describe svc mcp-server-service -n $NAMESPACE
}

cmd_top() {
    check_deployment
    echo -e "${PURPLE}📊 Resource Usage${NC}"
    
    if kubectl top nodes &> /dev/null; then
        echo -e "${CYAN}Node Usage:${NC}"
        kubectl top nodes
        echo
        
        echo -e "${CYAN}Pod Usage:${NC}"
        kubectl top pods -n $NAMESPACE
    else
        warning "Metrics server not available"
    fi
}

# Main command dispatcher
case "${1:-status}" in
    status)     cmd_status ;;
    logs)       cmd_logs "$@" ;;
    shell)      cmd_shell ;;
    scale)      cmd_scale "$@" ;;
    restart)    cmd_restart ;;
    forward)    cmd_forward "$@" ;;
    test)       cmd_test ;;
    delete)     cmd_delete ;;
    events)     cmd_events ;;
    describe)   cmd_describe ;;
    top)        cmd_top ;;
    help|--help|-h) show_usage ;;
    *)
        error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
