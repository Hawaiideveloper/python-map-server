#!/bin/bash

# MCP Server Connection Setup Script
# Supports: VSCode, Claude Desktop, Cursor IDE, and Custom Agents

echo "🔗 Python MCP Server Connection Setup"
echo "====================================="

# Get the service IP and port
NAMESPACE="python-mcp-server"
SERVICE_NAME="python-mcp-server-service"

echo "🔍 Getting service information..."
SERVICE_IP=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
SERVICE_PORT=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)
CLUSTER_IP=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
NODE_PORT=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null)

echo "📊 Service Information:"
echo "   Service IP: $SERVICE_IP"
echo "   Service Port: $SERVICE_PORT"
echo "   Cluster IP: $CLUSTER_IP"
echo "   Node Port: $NODE_PORT"

# Check if LoadBalancer has external IP
if [ -z "$SERVICE_IP" ] || [ "$SERVICE_IP" = "<pending>" ]; then
    echo "⚠️  LoadBalancer external IP not available"
    echo "💡 Using port-forward for local access..."
    
    # Set up port forwarding
    echo "🔄 Setting up port forwarding..."
    kubectl port-forward svc/$SERVICE_NAME 8080:80 -n $NAMESPACE &
    PORT_FORWARD_PID=$!
    sleep 3
    
    MCP_HOST="localhost"
    MCP_PORT="8080"
    MCP_URL="http://localhost:8080"
else
    MCP_HOST="$SERVICE_IP"
    MCP_PORT="$SERVICE_PORT"
    MCP_URL="http://$SERVICE_IP:$SERVICE_PORT"
fi

echo ""
echo "🎯 MCP Server Connection Details:"
echo "   Host: $MCP_HOST"
echo "   Port: $MCP_PORT"
echo "   URL: $MCP_URL"
echo ""

# Test connection
echo "🔍 Testing MCP Server connection..."
if curl -s "$MCP_URL/health" >/dev/null 2>&1; then
    echo "✅ MCP Server is responding!"
    curl -s "$MCP_URL/health" | jq . 2>/dev/null || curl -s "$MCP_URL/health"
else
    echo "❌ MCP Server is not responding"
    echo "💡 Check if the service is running: kubectl get pods -n $NAMESPACE"
fi

echo ""
echo "🔧 MCP Client Configuration Files:"
echo "=================================="

# Create VSCode configuration
echo "📝 Creating VSCode MCP configuration..."
mkdir -p ~/.vscode
cat > ~/.vscode/mcp-settings.json << EOF
{
  "mcp.servers": {
    "python-mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "ENVIRONMENT": "production",
        "HTTP_HOST": "0.0.0.0",
        "HTTP_PORT": "33221",
        "PYTHONPATH": "/app/src",
        "LOG_LEVEL": "info"
      }
    }
  }
}
EOF

# Create Claude Desktop configuration
echo "📝 Creating Claude Desktop MCP configuration..."
mkdir -p ~/Library/Application\ Support/Claude
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << EOF
{
  "mcpServers": {
    "python-mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "ENVIRONMENT": "production",
        "HTTP_HOST": "0.0.0.0",
        "HTTP_PORT": "33221",
        "PYTHONPATH": "/app/src",
        "LOG_LEVEL": "info"
      }
    }
  }
}
EOF

# Create Cursor IDE configuration
echo "📝 Creating Cursor IDE MCP configuration..."
mkdir -p ~/Library/Application\ Support/Cursor/User
cat > ~/Library/Application\ Support/Cursor/User/settings.json << EOF
{
  "mcp.servers": {
    "python-mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "ENVIRONMENT": "production",
        "HTTP_HOST": "0.0.0.0",
        "HTTP_PORT": "33221",
        "PYTHONPATH": "/app/src",
        "LOG_LEVEL": "info"
      }
    }
  }
}
EOF

# Create generic MCP client configuration
echo "📝 Creating generic MCP client configuration..."
cat > mcp-client-config.json << EOF
{
  "mcpServers": {
    "python-mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "ENVIRONMENT": "production",
        "HTTP_HOST": "0.0.0.0",
        "HTTP_PORT": "33221",
        "PYTHONPATH": "/app/src",
        "LOG_LEVEL": "info"
      }
    }
  }
}
EOF

# Create Docker-based MCP client configuration
echo "📝 Creating Docker-based MCP client configuration..."
cat > mcp-docker-config.json << EOF
{
  "mcpServers": {
    "python-mcp-server": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "ENVIRONMENT=production",
        "-e", "HTTP_HOST=0.0.0.0",
        "-e", "HTTP_PORT=33221",
        "-e", "PYTHONPATH=/app/src",
        "-e", "LOG_LEVEL=info",
        "ghcr.io/hawaiideveloper/python-mcp-server:latest"
      ]
    }
  }
}
EOF

# Create Kubernetes-based MCP client configuration
echo "📝 Creating Kubernetes-based MCP client configuration..."
cat > mcp-k8s-config.json << EOF
{
  "mcpServers": {
    "python-mcp-server": {
      "command": "kubectl",
      "args": [
        "exec", "-i", "-n", "python-mcp-server",
        "deployment/python-mcp-server",
        "--", "python", "-m", "mcp_server.server"
      ],
      "env": {
        "ENVIRONMENT": "production",
        "HTTP_HOST": "0.0.0.0",
        "HTTP_PORT": "33221",
        "PYTHONPATH": "/app/src",
        "LOG_LEVEL": "info"
      }
    }
  }
}
EOF

echo ""
echo "🎉 MCP Server Configuration Complete!"
echo "====================================="
echo ""
echo "📁 Configuration files created:"
echo "   • ~/.vscode/mcp-settings.json (VSCode)"
echo "   • ~/Library/Application Support/Claude/claude_desktop_config.json (Claude Desktop)"
echo "   • ~/Library/Application Support/Cursor/User/settings.json (Cursor IDE)"
echo "   • mcp-client-config.json (Generic MCP client)"
echo "   • mcp-docker-config.json (Docker-based client)"
echo "   • mcp-k8s-config.json (Kubernetes-based client)"
echo ""
echo "🔗 Connection Details:"
echo "   • Host: $MCP_HOST"
echo "   • Port: $MCP_PORT"
echo "   • URL: $MCP_URL"
echo ""
echo "🚀 Next Steps:"
echo "   1. Restart your MCP client (VSCode, Claude Desktop, Cursor)"
echo "   2. The MCP server should now be available in your client"
echo "   3. Test the connection using the health endpoint: $MCP_URL/health"
echo ""
echo "🔧 Troubleshooting:"
echo "   • Check pod status: kubectl get pods -n $NAMESPACE"
echo "   • Check service status: kubectl get svc -n $NAMESPACE"
echo "   • Check logs: kubectl logs -n $NAMESPACE -l app=python-mcp-server"
echo "   • Test health: curl $MCP_URL/health"
echo ""

# Clean up port forwarding if we started it
if [ ! -z "$PORT_FORWARD_PID" ]; then
    echo "🔄 Port forwarding is running in background (PID: $PORT_FORWARD_PID)"
    echo "💡 To stop port forwarding: kill $PORT_FORWARD_PID"
fi