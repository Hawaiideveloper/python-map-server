#!/bin/bash

# Script to test the new GitHub token with GHCR permissions
echo "🧪 Testing New GitHub Token with GHCR Permissions"
echo "==============================================="

# Check if PYTHON_MCP_SERVER_GHCR_TOKEN is set
if [ -z "$PYTHON_MCP_SERVER_GHCR_TOKEN" ]; then
    echo "❌ PYTHON_MCP_SERVER_GHCR_TOKEN not found in environment."
    echo "💡 Please source your zshrc file: source ~/.zshrc"
    exit 1
fi

export GITHUB_TOKEN="$PYTHON_MCP_SERVER_GHCR_TOKEN"
echo "✅ Testing token: ...${GITHUB_TOKEN: -4} (last 4 chars)"

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

# Check token permissions
echo "🔍 Checking token permissions..."
PERMISSIONS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | jq -r '.permissions // "No permissions info"')
echo "Token permissions: $PERMISSIONS"

# Test GHCR authentication
echo "🔍 Testing GHCR authentication..."
GHCR_RESPONSE=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $GITHUB_TOKEN" https://ghcr.io/v2/ -o /dev/null)

if [ "$GHCR_RESPONSE" = "200" ]; then
    echo "✅ GHCR authentication successful!"
    
    # Test Docker login to GHCR
    echo "🔍 Testing Docker login to GHCR..."
    echo "$GITHUB_TOKEN" | docker login ghcr.io -u hawaiideveloper --password-stdin >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker login to GHCR successful!"
        echo ""
        echo "🎉 Your token has the correct GHCR permissions!"
        echo ""
        echo "🚀 Now you can:"
        echo "   1. Push the image: ./push-to-ghcr.sh"
        echo "   2. Deploy to Kubernetes: ./replace-deployment-from-working-terminal.sh"
    else
        echo "❌ Docker login to GHCR failed!"
        echo "💡 Token might not have 'write:packages' scope"
    fi
else
    echo "❌ GHCR authentication failed! (HTTP $GHCR_RESPONSE)"
    echo "💡 Token needs 'read:packages' and 'write:packages' scopes"
    echo ""
    echo "🔧 Please create a new token with these scopes:"
    echo "   • repo"
    echo "   • write:packages"
    echo "   • read:packages"
    echo "   • delete:packages"
fi