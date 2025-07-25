#!/bin/bash

# Railway MCP Server Command Line Interface
# Controls the deployed MCP server via Railway's API and HTTP endpoints

set -e

# Configuration
BASE_URL="https://python-mcp-server-production.up.railway.app"
ADMIN_KEY="mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs"
HEADERS="Content-Type: application/json"
AUTH_HEADER="X-Admin-Key: $ADMIN_KEY"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Show usage
show_usage() {
    echo "🚀 Railway MCP Server CLI"
    echo "========================="
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  status              Check server health and status"
    echo "  info                Get detailed server information"
    echo "  tools               List available MCP tools"
    echo "  logs                View recent server logs"
    echo "  exec <code>         Execute Python code on the server"
    echo "  lint <file>         Lint Python code"
    echo "  format <file>       Format Python code"
    echo "  test <file>         Run tests on Python code"
    echo "  system              Get system information"
    echo "  deploy              Trigger a new deployment"
    echo "  scale <replicas>    Scale the service (Railway Pro feature)"
    echo "  env                 Manage environment variables"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 exec \"print('Hello from Railway!')\""
    echo "  $0 lint main.py"
    echo "  $0 system"
    echo ""
}

# Check server status
check_status() {
    log_info "Checking server status..."
    
    response=$(curl -s -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/health")
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        log_success "Server is healthy"
        echo "$body" | jq -r '"Status: " + .status + " | Version: " + .version + " | Uptime: " + .uptime'
    else
        log_error "Server health check failed (HTTP $http_code)"
        echo "$body"
        exit 1
    fi
}

# Get server info
get_info() {
    log_info "Getting server information..."
    
    response=$(curl -s -H "$AUTH_HEADER" "$BASE_URL/")
    echo "$response" | jq '.'
}

# List tools
list_tools() {
    log_info "Listing available MCP tools..."
    
    response=$(curl -s -H "$AUTH_HEADER" "$BASE_URL/")
    echo "$response" | jq -r '.endpoints | to_entries[] | "• " + .key + ": " + .value'
}

# Execute Python code
execute_code() {
    local code="$1"
    if [ -z "$code" ]; then
        log_error "No code provided"
        echo "Usage: $0 exec \"<python_code>\""
        exit 1
    fi
    
    log_info "Executing Python code..."
    
    response=$(curl -s -X POST "$BASE_URL/run_code" \
        -H "$AUTH_HEADER" \
        -H "$HEADERS" \
        -d "{\"code\": $(echo "$code" | jq -R .)}")
    
    status=$(echo "$response" | jq -r '.status')
    if [ "$status" = "success" ]; then
        log_success "Code executed successfully"
        echo "$response" | jq -r '.result.stdout'
        if [ "$(echo "$response" | jq -r '.result.stderr')" != "null" ] && [ "$(echo "$response" | jq -r '.result.stderr')" != "" ]; then
            log_warning "stderr:"
            echo "$response" | jq -r '.result.stderr'
        fi
    else
        log_error "Code execution failed"
        echo "$response" | jq -r '.error'
    fi
}

# Lint code file
lint_code() {
    local file="$1"
    if [ -z "$file" ] || [ ! -f "$file" ]; then
        log_error "File not found: $file"
        exit 1
    fi
    
    log_info "Linting code file: $file"
    
    code=$(cat "$file")
    response=$(curl -s -X POST "$BASE_URL/lint_code" \
        -H "$AUTH_HEADER" \
        -H "$HEADERS" \
        -d "{\"code\": $(echo "$code" | jq -R -s .)}")
    
    status=$(echo "$response" | jq -r '.status')
    if [ "$status" = "success" ]; then
        issues=$(echo "$response" | jq -r '.result.issues | length')
        if [ "$issues" = "0" ]; then
            log_success "No linting issues found"
        else
            log_warning "$issues linting issues found"
            echo "$response" | jq -r '.result.issues[] | "Line " + (.line | tostring) + ": " + .message'
        fi
    else
        log_error "Linting failed"
        echo "$response" | jq -r '.error'
    fi
}

# Format code file
format_code() {
    local file="$1"
    if [ -z "$file" ] || [ ! -f "$file" ]; then
        log_error "File not found: $file"
        exit 1
    fi
    
    log_info "Formatting code file: $file"
    
    code=$(cat "$file")
    response=$(curl -s -X POST "$BASE_URL/format_code" \
        -H "$AUTH_HEADER" \
        -H "$HEADERS" \
        -d "{\"code\": $(echo "$code" | jq -R -s .)}")
    
    status=$(echo "$response" | jq -r '.status')
    if [ "$status" = "success" ]; then
        log_success "Code formatted successfully"
        echo "$response" | jq -r '.result.formatted_code' > "$file.formatted"
        log_info "Formatted code saved to: $file.formatted"
    else
        log_error "Formatting failed"
        echo "$response" | jq -r '.error'
    fi
}

# Test code file
test_code() {
    local file="$1"
    if [ -z "$file" ] || [ ! -f "$file" ]; then
        log_error "File not found: $file"
        exit 1
    fi
    
    log_info "Testing code file: $file"
    
    code=$(cat "$file")
    response=$(curl -s -X POST "$BASE_URL/test_code" \
        -H "$AUTH_HEADER" \
        -H "$HEADERS" \
        -d "{\"code\": $(echo "$code" | jq -R -s .)}")
    
    status=$(echo "$response" | jq -r '.status')
    if [ "$status" = "success" ]; then
        log_success "Tests completed"
        echo "$response" | jq -r '.result'
    else
        log_error "Testing failed"
        echo "$response" | jq -r '.error'
    fi
}

# Get system information
get_system_info() {
    log_info "Getting system information..."
    
    response=$(curl -s -H "$AUTH_HEADER" "$BASE_URL/system/info")
    status=$(echo "$response" | jq -r '.status')
    
    if [ "$status" = "success" ]; then
        log_success "System information retrieved"
        echo "$response" | jq -r '.result | 
            "CPU: " + (.cpu.cpu_count | tostring) + " cores (" + (.cpu.cpu_percent | tostring) + "% usage)" +
            "\nMemory: " + (.memory.total_gb | tostring) + "GB total (" + (.memory.percent | tostring) + "% used)" +
            "\nDisk: " + (.disk.total_gb | tostring) + "GB total (" + (.disk.percent | tostring) + "% used)" +
            "\nPython: " + .python.version +
            "\nPackages: " + (.python.packages | length | tostring) + " installed"'
    else
        log_error "Failed to get system information"
        echo "$response" | jq -r '.error'
    fi
}

# Trigger deployment via git
trigger_deployment() {
    log_info "Triggering new deployment..."
    
    if [ ! -d ".git" ]; then
        log_error "Not in a git repository"
        exit 1
    fi
    
    # Create deployment trigger
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "Deployment triggered at: $timestamp" > deployment_trigger.txt
    
    git add deployment_trigger.txt
    git commit -m "Trigger deployment - $timestamp"
    git push origin main
    
    if [ $? -eq 0 ]; then
        log_success "Deployment triggered successfully"
        log_info "Railway will automatically deploy the changes"
        log_info "Check Railway dashboard for deployment status"
    else
        log_error "Failed to trigger deployment"
        exit 1
    fi
}

# Railway CLI commands (requires Railway CLI)
railway_scale() {
    local replicas="$1"
    if [ -z "$replicas" ]; then
        log_error "Number of replicas not specified"
        echo "Usage: $0 scale <replicas>"
        exit 1
    fi
    
    if ! command -v railway &> /dev/null; then
        log_error "Railway CLI not installed"
        log_info "Install with: curl -fsSL https://railway.app/install.sh | sh"
        exit 1
    fi
    
    log_info "Scaling service to $replicas replicas..."
    railway scale --replicas "$replicas"
}

# View logs (requires Railway CLI)
view_logs() {
    if ! command -v railway &> /dev/null; then
        log_error "Railway CLI not installed"
        log_info "Install with: curl -fsSL https://railway.app/install.sh | sh"
        exit 1
    fi
    
    log_info "Viewing recent logs..."
    railway logs --tail 100
}

# Manage environment variables
manage_env() {
    if ! command -v railway &> /dev/null; then
        log_error "Railway CLI not installed"
        log_info "Install with: curl -fsSL https://railway.app/install.sh | sh"
        exit 1
    fi
    
    log_info "Current environment variables:"
    railway variables
}

# Main command dispatcher
case "${1:-}" in
    "status")
        check_status
        ;;
    "info")
        get_info
        ;;
    "tools")
        list_tools
        ;;
    "exec")
        execute_code "$2"
        ;;
    "lint")
        lint_code "$2"
        ;;
    "format")
        format_code "$2"
        ;;
    "test")
        test_code "$2"
        ;;
    "system")
        get_system_info
        ;;
    "deploy")
        trigger_deployment
        ;;
    "scale")
        railway_scale "$2"
        ;;
    "logs")
        view_logs
        ;;
    "env")
        manage_env
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    "")
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
