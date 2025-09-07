#!/bin/bash

# Script to push the latest image to GitHub Container Registry
echo "🚀 Pushing Latest Image to GitHub Container Registry"
echo "================================================="

# Check if PYTHON_MCP_SERVER_GHCR_TOKEN is set
if [ -z "$PYTHON_MCP_SERVER_GHCR_TOKEN" ]; then
    echo "❌ PYTHON_MCP_SERVER_GHCR_TOKEN not found in environment."
    echo "💡 Please source your zshrc file: source ~/.zshrc"
    exit 1
fi

export GITHUB_TOKEN="$PYTHON_MCP_SERVER_GHCR_TOKEN"
echo "✅ Using token: ...${GITHUB_TOKEN: -4} (last 4 chars)"

# Test GitHub API
echo "🔍 Testing GitHub API access..."
USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
USER_LOGIN=$(echo $USER_INFO | jq -r '.login // "null"')

if [ "$USER_LOGIN" != "null" ] && [ "$USER_LOGIN" != "" ]; then
    echo "✅ GitHub API authentication successful!"
    echo "User: $USER_LOGIN"
else
    echo "❌ GitHub API authentication failed!"
    exit 1
fi

# Check if local image exists
echo "🔍 Checking local image..."
if ! docker images | grep -q "hawaiideveloper/python-mcp-server.*latest"; then
    echo "❌ Local image not found!"
    echo "💡 Please build the image first:"
    echo "   docker build -t hawaiideveloper/python-mcp-server:latest ."
    exit 1
fi

echo "✅ Local image found:"
docker images | grep "hawaiideveloper/python-mcp-server.*latest"

# Login to GitHub Container Registry
echo "🔐 Logging in to GitHub Container Registry..."
echo "$GITHUB_TOKEN" | docker login ghcr.io -u hawaiideveloper --password-stdin

if [ $? -eq 0 ]; then
    echo "✅ Successfully logged in to GHCR"
else
    echo "❌ Failed to login to GHCR"
    exit 1
fi

# Tag the image for GHCR
echo "🏷️  Tagging image for GHCR..."
docker tag hawaiideveloper/python-mcp-server:latest ghcr.io/hawaiideveloper/python-mcp-server:latest

# Push the image
echo "📤 Pushing image to GHCR..."
docker push ghcr.io/hawaiideveloper/python-mcp-server:latest

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed image to GHCR!"
    echo ""
    echo "🎉 Image is now available at:"
    echo "   ghcr.io/hawaiideveloper/python-mcp-server:latest"
    echo ""
    echo "🔍 You can verify it's there by visiting:"
    echo "   https://github.com/hawaiideveloper/python-mcp-server/pkgs/container/python-mcp-server"
    echo ""
    echo "🚀 Now you can run the Kubernetes deployment!"
else
    echo "❌ Failed to push image to GHCR"
    exit 1
fi