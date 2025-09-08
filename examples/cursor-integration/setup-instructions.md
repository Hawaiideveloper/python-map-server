# 🚀 Cursor Integration Setup

## Quick Setup for Cursor IDE

### 1. **Copy the WebSocket Bridge**
```bash
cp examples/cursor-integration/mcp-websocket-bridge.example.py mcp-websocket-bridge.py
```

### 2. **Update the Configuration**
Edit `mcp-websocket-bridge.py` and replace:
- `YOUR_K8S_IP` → Your Kubernetes cluster IP
- `YOUR_PORT` → Your MCP service port (usually 32556 for NodePort)

### 3. **Configure Cursor**
Copy the example configuration:
```bash
cp examples/cursor-integration/cursor-mcp-config.example.json ~/.cursor/mcp_servers.json
```

Update the path in the config file to point to your `mcp-websocket-bridge.py` location.

### 4. **Restart Cursor**
Close and reopen Cursor. You should see "Python Expert (Kubernetes)" in your MCP servers.

### 5. **Test Connection**
1. Open any Python file
2. Press `Ctrl+Shift+P` → "MCP: Execute Python Code"
3. Or right-click → "Generate Tests"

## Available Features
- ✅ **60+ Expert Python Tools**
- ✅ **Code Execution & Analysis**
- ✅ **JSON/YAML Processing (13 tools)**
- ✅ **AI-Powered Development**
- ✅ **Security Scanning**
- ✅ **Performance Profiling**
- ✅ **Smart Refactoring**
