#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")/../../.."

echo "🐳 Starting Python MCP Server in Docker..."
echo "📁 Working directory: $(pwd)"

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t python-mcp-server:latest .

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image."
    exit 1
fi

# Stop any existing container with the same name
echo "🛑 Stopping existing container (if any)..."
docker stop python-mcp-server 2>/dev/null || true
docker rm python-mcp-server 2>/dev/null || true

# Start the Docker container in detached mode
echo "🚀 Starting container in detached mode..."
docker run -d \
    --name python-mcp-server \
    -p 3011:3011 \
    -e PORT=3011 \
    --restart unless-stopped \
    python-mcp-server:latest

# Check if the container started successfully
if [ $? -eq 0 ]; then
    echo "✅ Docker container started successfully in detached mode."
    
    # Wait a moment for the server to start
    echo "⏳ Waiting for server to start..."
    sleep 5
    
    # Test the health endpoint
    echo "🏥 Checking server health..."
    if curl -f http://localhost:3011/health 2>/dev/null; then
        echo "🎉 MCP Server is running and healthy!"
        echo "📡 HTTP API available at: http://localhost:3011"
        echo "📊 Admin dashboard: http://localhost:3011/admin"
        echo "💾 Health check: http://localhost:3011/health"
    else
        echo "⚠️  Server started but health check failed. It may still be starting up."
        echo "📝 Check logs with: docker logs python-mcp-server"
    fi
    
    echo ""
    echo "📋 Container status:"
    docker ps --filter "name=python-mcp-server"
    
    echo ""
    echo "🎛️  Useful commands:"
    echo "  • View logs: docker logs python-mcp-server"
    echo "  • Follow logs: docker logs -f python-mcp-server"
    echo "  • Stop server: docker stop python-mcp-server"
    echo "  • Restart server: docker restart python-mcp-server"
    
else
    echo "❌ Failed to start the Docker container."
    echo "📝 Check Docker daemon status and try again."
    exit 1
fi