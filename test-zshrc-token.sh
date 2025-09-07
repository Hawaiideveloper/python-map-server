#!/bin/bash

# Script to test the GitHub token from zshrc
echo "🧪 Testing GitHub Token from zshrc"
echo "================================="

# Check if PYTHON_MCP_SERVER_GHCR_TOKEN is set
if [ -z "$PYTHON_MCP_SERVER_GHCR_TOKEN" ]; then
    echo "❌ PYTHON_MCP_SERVER_GHCR_TOKEN not found in environment."
    echo "💡 Please source your zshrc file:"
    echo "   source ~/.zshrc"
    echo "   then run this script again"
    exit 1
fi

echo "✅ Found PYTHON_MCP_SERVER_GHCR_TOKEN: ${PYTHON_MCP_SERVER_GHCR_TOKEN:0:10}..."

# Test token with GitHub API
echo "🔍 Testing GitHub API access..."
USER_INFO=$(curl -s -H "Authorization: token $PYTHON_MCP_SERVER_GHCR_TOKEN" https://api.github.com/user)
USER_LOGIN=$(echo $USER_INFO | jq -r '.login // "null"')

if [ "$USER_LOGIN" != "null" ] && [ "$USER_LOGIN" != "" ]; then
    echo "✅ GitHub API authentication successful!"
    echo "User: $USER_LOGIN"
    
    # Check token scopes
    TOKEN_SCOPES=$(curl -s -H "Authorization: token $PYTHON_MCP_SERVER_GHCR_TOKEN" https://api.github.com/user | jq -r '.permissions // "No permissions info"')
    echo "Token scopes: $TOKEN_SCOPES"
    
    echo ""
    echo "🎉 Your new token is working! Now run:"
    echo "   ./test-new-token.sh"
    echo ""
    echo "This will update Kubernetes with your new token and fix the deployment."
    
else
    echo "❌ GitHub API authentication failed!"
    echo "Response: $USER_INFO"
    echo ""
    echo "💡 Please check your token in ~/.zshrc:"
    echo "   echo \$PYTHON_MCP_SERVER_GHCR_TOKEN"
    echo "   source ~/.zshrc"
fi