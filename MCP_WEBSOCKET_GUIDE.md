# 🚀 MCP Protocol Configuration Examples

## WebSocket MCP Client Connection

Your Python MCP server now supports **true MCP protocol** via WebSocket!

### **Railway Production URL:**
```
WebSocket MCP: wss://python-mcp-server-production.up.railway.app/mcp
HTTP REST API: https://python-mcp-server-production.up.railway.app/
```

### **Local Development URLs:**
```
WebSocket MCP: ws://localhost:8080/mcp
stdin/stdout MCP: Available in development mode
HTTP REST API: http://localhost:8080/
```

## Claude Desktop Configuration

Add this to your Claude Desktop MCP settings:

### **Option 1: WebSocket MCP (Recommended)**
```json
{
  "mcpServers": {
    "python-server": {
      "command": "node",
      "args": ["-e", "
        const WebSocket = require('ws');
        const ws = new WebSocket('wss://python-mcp-server-production.up.railway.app/mcp');
        
        ws.on('open', () => {
          process.stdin.on('data', (data) => {
            ws.send(data.toString());
          });
        });
        
        ws.on('message', (data) => {
          process.stdout.write(data.toString());
        });
        
        ws.on('error', (error) => {
          console.error('WebSocket error:', error);
        });
      "]
    }
  }
}
```

### **Option 2: HTTP Bridge**
```json
{
  "mcpServers": {
    "python-server-http": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "https://python-mcp-server-production.up.railway.app/mcp/bridge",
        "-H", "Content-Type: application/json",
        "-H", "Authorization: Bearer mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs",
        "-d", "@-"
      ]
    }
  }
}
```

## Python MCP Client

```python
import asyncio
import json
import websockets

class MCPClient:
    """WebSocket MCP client for Python."""
    
    def __init__(self, uri: str):
        self.uri = uri
        self.request_id = 0
    
    async def connect(self):
        """Connect to MCP server."""
        self.websocket = await websockets.connect(self.uri)
        
        # Initialize MCP connection
        await self.initialize()
    
    async def initialize(self):
        """Send MCP initialize request."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    }
                },
                "clientInfo": {
                    "name": "python-mcp-client",
                    "version": "1.0.0"
                }
            }
        }
        
        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        print("Initialize response:", json.loads(response))
        
        # Send initialized notification
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self.websocket.send(json.dumps(notification))
    
    async def list_tools(self):
        """List available tools."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
        }
        
        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        return json.loads(response)
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call a specific tool."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        return json.loads(response)
    
    def _next_id(self):
        """Generate next request ID."""
        self.request_id += 1
        return self.request_id
    
    async def close(self):
        """Close connection."""
        await self.websocket.close()

# Usage example
async def main():
    # Connect to Railway MCP server
    client = MCPClient("wss://python-mcp-server-production.up.railway.app/mcp")
    
    try:
        await client.connect()
        
        # List available tools
        tools = await client.list_tools()
        print("Available tools:", tools)
        
        # Execute Python code
        result = await client.call_tool("run_python_tool", {
            "code": "print('Hello from MCP WebSocket!'); import numpy as np; print(f'NumPy: {np.__version__}')"
        })
        print("Code execution result:", result)
        
        # Get system info
        system_info = await client.call_tool("system_info_tool", {})
        print("System info:", system_info)
        
    finally:
        await client.close()

# Run the client
if __name__ == "__main__":
    asyncio.run(main())
```

## JavaScript/Node.js MCP Client

```javascript
const WebSocket = require('ws');

class MCPClient {
    constructor(uri) {
        this.uri = uri;
        this.requestId = 0;
    }

    async connect() {
        this.ws = new WebSocket(this.uri);
        
        return new Promise((resolve, reject) => {
            this.ws.on('open', async () => {
                console.log('Connected to MCP server');
                await this.initialize();
                resolve();
            });
            
            this.ws.on('error', reject);
        });
    }

    async initialize() {
        const request = {
            jsonrpc: "2.0",
            id: this.nextId(),
            method: "initialize",
            params: {
                protocolVersion: "2024-11-05",
                capabilities: {
                    tools: { listChanged: true }
                },
                clientInfo: {
                    name: "nodejs-mcp-client",
                    version: "1.0.0"
                }
            }
        };

        this.send(request);
        
        // Send initialized notification
        setTimeout(() => {
            this.send({
                jsonrpc: "2.0",
                method: "notifications/initialized"
            });
        }, 100);
    }

    async listTools() {
        const request = {
            jsonrpc: "2.0",
            id: this.nextId(),
            method: "tools/list"
        };

        return this.sendAndWait(request);
    }

    async callTool(toolName, arguments) {
        const request = {
            jsonrpc: "2.0",
            id: this.nextId(),
            method: "tools/call",
            params: {
                name: toolName,
                arguments: arguments
            }
        };

        return this.sendAndWait(request);
    }

    send(message) {
        this.ws.send(JSON.stringify(message));
    }

    sendAndWait(request) {
        return new Promise((resolve, reject) => {
            const handler = (data) => {
                const response = JSON.parse(data);
                if (response.id === request.id) {
                    this.ws.off('message', handler);
                    if (response.error) {
                        reject(new Error(response.error.message));
                    } else {
                        resolve(response.result);
                    }
                }
            };

            this.ws.on('message', handler);
            this.send(request);

            // Timeout after 30 seconds
            setTimeout(() => {
                this.ws.off('message', handler);
                reject(new Error('Request timeout'));
            }, 30000);
        });
    }

    nextId() {
        return ++this.requestId;
    }

    close() {
        this.ws.close();
    }
}

// Usage
async function main() {
    const client = new MCPClient('wss://python-mcp-server-production.up.railway.app/mcp');
    
    try {
        await client.connect();
        
        // List tools
        const tools = await client.listTools();
        console.log('Available tools:', tools);
        
        // Execute Python code
        const result = await client.callTool('run_python_tool', {
            code: 'import sys; print(f"Python {sys.version}"); print("Hello from Node.js MCP client!")'
        });
        console.log('Execution result:', result);
        
    } catch (error) {
        console.error('Error:', error);
    } finally {
        client.close();
    }
}

main();
```

## Testing Your MCP Server

### **1. Test WebSocket MCP Connection**
```bash
# Test WebSocket connection
npm install -g wscat
wscat -c wss://python-mcp-server-production.up.railway.app/mcp

# Send MCP initialize request
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":true}},"clientInfo":{"name":"test-client","version":"1.0.0"}}}

# Send tools/list request
{"jsonrpc":"2.0","id":2,"method":"tools/list"}

# Execute Python code
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"run_python_tool","arguments":{"code":"print('Hello MCP!')"}}}
```

### **2. Test HTTP REST API**
```bash
# Health check
curl https://python-mcp-server-production.up.railway.app/health

# Execute code via HTTP
curl -X POST https://python-mcp-server-production.up.railway.app/run_code \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs" \
  -d '{"code": "print(\"Hello HTTP!\")"}'
```

## 🎉 **Your Server Now Supports:**

✅ **True MCP Protocol** via WebSocket (JSON-RPC 2.0)  
✅ **HTTP REST API** for web clients  
✅ **Backward compatibility** with existing clients  
✅ **Railway deployment** with both protocols  
✅ **Claude Desktop integration** ready  
✅ **Custom MCP clients** supported  

**Your MCP server is now a true MCP server! 🚀**
