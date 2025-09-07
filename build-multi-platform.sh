#!/bin/bash

# Script to build and push multi-platform image for Kubernetes
echo "🏗️  Building Multi-Platform Image for Kubernetes"
echo "=============================================="

# Check if PYTHON_MCP_SERVER_GHCR_TOKEN is set
if [ -z "$PYTHON_MCP_SERVER_GHCR_TOKEN" ]; then
    echo "❌ PYTHON_MCP_SERVER_GHCR_TOKEN not found in environment."
    echo "💡 Please source your zshrc file: source ~/.zshrc"
    exit 1
fi

export GITHUB_TOKEN="$PYTHON_MCP_SERVER_GHCR_TOKEN"
echo "✅ Using token: ...${GITHUB_TOKEN: -4} (last 4 chars)"

# Login to GHCR
echo "🔐 Logging in to GitHub Container Registry..."
echo "$GITHUB_TOKEN" | docker login ghcr.io -u hawaiideveloper --password-stdin

if [ $? -eq 0 ]; then
    echo "✅ Successfully logged in to GHCR"
else
    echo "❌ Failed to login to GHCR"
    exit 1
fi

# Build and push multi-platform image
echo "🏗️  Building multi-platform image..."
echo "🔍 Platforms: linux/amd64, linux/arm64"

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag ghcr.io/hawaiideveloper/python-mcp-server:latest \
    --push \
    .

if [ $? -eq 0 ]; then
    echo "✅ Multi-platform image built and pushed successfully!"
    echo "🎉 Image now supports both AMD64 and ARM64 architectures"
    echo ""
    echo "🔍 You can now deploy to Kubernetes:"
    echo "   kubectl apply -f k8s-production-deployment.yaml"
else
    echo "❌ Failed to build multi-platform image"
    exit 1
fi