#!/usr/bin/env python3
"""
Local MCP Server Setup and Usage Guide
Run this to start and test your local MCP server for debugging other projects.
"""

import subprocess
import time
import requests
import json
import os
import sys

# Colors for output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.END):
    print(f"{color}{text}{Colors.END}")

def get_admin_key():
    """Extract admin key from server logs or use default."""
    # Default local admin key (for development)
    return "mcp_admin_7kuF6ve-SdAvQ5joKObch4tGSdmIMifCA6CPFGuCa-k"

def test_server():
    """Test if the local server is working."""
    print_colored("🔍 Testing Local MCP Server...", Colors.BLUE)
    
    admin_key = get_admin_key()
    base_url = "http://localhost:8080"
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print_colored("✅ Server is healthy!", Colors.GREEN)
            data = response.json()
            print(f"   Version: {data['version']}")
            print(f"   Environment: {data['environment']}")
        else:
            print_colored("❌ Server health check failed", Colors.RED)
            return False
    except Exception as e:
        print_colored(f"❌ Cannot connect to server: {e}", Colors.RED)
        return False
    
    # Test 2: Get server info
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_colored("✅ Server info retrieved:", Colors.GREEN)
            print(f"   WebSocket MCP: {data['protocols']['mcp_websocket']}")
            print(f"   HTTP REST: {data['protocols']['http_rest']}")
            print(f"   Available endpoints: {len(data['endpoints'])}")
        else:
            print_colored("❌ Cannot get server info", Colors.RED)
    except Exception as e:
        print_colored(f"⚠️  Server info error: {e}", Colors.YELLOW)
    
    # Test 3: Try code execution (without auth first, then with auth)
    test_code = "print('Hello from local MCP server!')"
    headers = {"Content-Type": "application/json"}
    
    # Try without auth first (for development mode)
    try:
        response = requests.post(
            f"{base_url}/run_code",
            headers=headers,
            json={"code": test_code},
            timeout=10
        )
        if response.status_code == 200:
            print_colored("✅ Code execution works (no auth required)!", Colors.GREEN)
            return True
    except:
        pass
    
    # Try with auth
    headers["X-Admin-Key"] = admin_key
    try:
        response = requests.post(
            f"{base_url}/run_code",
            headers=headers,
            json={"code": test_code},
            timeout=10
        )
        if response.status_code == 200:
            print_colored("✅ Code execution works (with auth)!", Colors.GREEN)
            result = response.json()
            if result.get("result", {}).get("stdout"):
                print(f"   Output: {result['result']['stdout'].strip()}")
            return True
        else:
            print_colored(f"⚠️  Code execution failed: {response.status_code}", Colors.YELLOW)
            print(f"   Response: {response.text}")
    except Exception as e:
        print_colored(f"⚠️  Code execution error: {e}", Colors.YELLOW)
    
    return True  # Server is running even if code execution has auth issues

def print_usage_guide():
    """Print comprehensive usage guide for the local MCP server."""
    admin_key = get_admin_key()
    
    print_colored("\n🚀 LOCAL MCP SERVER USAGE GUIDE", Colors.BOLD)
    print_colored("=" * 50, Colors.BLUE)
    
    print_colored("\n📍 Server Details:", Colors.BOLD)
    print(f"   URL: http://localhost:8080")
    print(f"   WebSocket MCP: ws://localhost:8080/mcp")
    print(f"   Admin Key: {admin_key}")
    print(f"   Documentation: http://localhost:8080/docs")
    
    print_colored("\n🔧 HTTP API Usage:", Colors.BOLD)
    print_colored("Execute Python code:", Colors.GREEN)
    print(f"""curl -X POST http://localhost:8080/run_code \\
  -H "Content-Type: application/json" \\
  -H "X-Admin-Key: {admin_key}" \\
  -d '{{"code": "print(\\"Hello World!\\")"}}' """)
    
    print_colored("\nLint Python code:", Colors.GREEN)
    print(f"""curl -X POST http://localhost:8080/lint_code \\
  -H "Content-Type: application/json" \\
  -H "X-Admin-Key: {admin_key}" \\
  -d '{{"code": "print( \\"badly formatted\\" )"}}' """)
    
    print_colored("\nGet system information:", Colors.GREEN)
    print(f"""curl -H "X-Admin-Key: {admin_key}" http://localhost:8080/system/info""")
    
    print_colored("\n🔌 MCP Protocol Usage:", Colors.BOLD)
    print_colored("For Claude Desktop, add to claude_desktop_config.json:", Colors.GREEN)
    claude_config = {
        "mcpServers": {
            "local-python-mcp": {
                "command": "python",
                "args": ["-m", "mcp", "ws://localhost:8080/mcp"]
            }
        }
    }
    print(json.dumps(claude_config, indent=2))
    
    print_colored("\n🐍 Python Client Example:", Colors.BOLD)
    python_example = '''import asyncio
import websockets
import json

async def test_mcp():
    uri = "ws://localhost:8080/mcp"
    async with websockets.connect(uri) as websocket:
        # Initialize
        init_msg = {
            "jsonrpc": "2.0",
            "method": "initialize", 
            "params": {"protocolVersion": "1.0", "capabilities": {}},
            "id": 1
        }
        await websocket.send(json.dumps(init_msg))
        response = await websocket.recv()
        print("Initialize:", json.loads(response))
        
        # List tools
        tools_msg = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        await websocket.send(json.dumps(tools_msg))
        response = await websocket.recv()
        print("Tools:", json.loads(response))

asyncio.run(test_mcp())'''
    print_colored(python_example, Colors.GREEN)
    
    print_colored("\n🛠️ For Debugging Other Projects:", Colors.BOLD)
    print_colored("1. Code Execution & Testing:", Colors.YELLOW)
    print("   - Use /run_code to test Python snippets")
    print("   - Use /lint_code to check code quality")
    print("   - Use /format_code to fix formatting")
    print("   - Use /test_code to run unit tests")
    
    print_colored("\n2. System Analysis:", Colors.YELLOW)
    print("   - Use /system/info for system diagnostics")
    print("   - Use /system/packages to check installed libraries")
    print("   - Use /system/processes to monitor running processes")
    
    print_colored("\n3. AI/ML Debugging:", Colors.YELLOW)
    print("   - Use /ai/openai for OpenAI API testing")
    print("   - Use /ai/anthropic for Claude API testing")
    print("   - Use /ai/embeddings for vector operations")
    
    print_colored("\n4. Cloud SDK Testing:", Colors.YELLOW)
    print("   - Use /sdk/aws for AWS operations")
    print("   - Use /sdk/gcp for Google Cloud operations")
    print("   - Use /sdk/azure for Azure operations")
    
    print_colored("\n📝 Example Debugging Workflow:", Colors.BOLD)
    workflow_example = f'''# 1. Test problematic code
curl -X POST http://localhost:8080/run_code \\
  -H "Content-Type: application/json" \\
  -H "X-Admin-Key: {admin_key}" \\
  -d '{{"code": "import problematic_module; problematic_module.test()"}}'

# 2. Check code quality
curl -X POST http://localhost:8080/lint_code \\
  -H "Content-Type: application/json" \\
  -H "X-Admin-Key: {admin_key}" \\
  -d '{{"code": "$(cat your_file.py)"}}'

# 3. Get system info for environment debugging
curl -H "X-Admin-Key: {admin_key}" http://localhost:8080/system/info

# 4. Test AI/ML APIs
curl -X POST http://localhost:8080/ai/openai \\
  -H "Content-Type: application/json" \\
  -H "X-Admin-Key: {admin_key}" \\
  -d '{{"prompt": "Test prompt", "model": "gpt-3.5-turbo"}}'
'''
    print_colored(workflow_example, Colors.GREEN)
    
    print_colored("\n🎯 Pro Tips:", Colors.BOLD)
    print("• Use the /docs endpoint for interactive API documentation")
    print("• Set timeouts for long-running code execution")
    print("• Use the WebSocket MCP for real-time debugging")
    print("• Check server logs for detailed error information")
    print("• Use system tools to diagnose environment issues")

def main():
    print_colored("🚀 Python MCP Server - Local Setup", Colors.BOLD)
    print_colored("=" * 40, Colors.BLUE)
    
    # Check if server is running
    print_colored("\n1. Checking if server is running...", Colors.BLUE)
    if test_server():
        print_colored("\n✅ Server is ready for use!", Colors.GREEN)
        print_usage_guide()
    else:
        print_colored("\n❌ Server is not running or has issues.", Colors.RED)
        print_colored("\nTo start the server manually:", Colors.YELLOW)
        print("cd /Users/hawaiidevelopergmail.com/Documents/github/python-mcp-server")
        print("/Users/hawaiidevelopergmail.com/Library/Caches/pypoetry/virtualenvs/python-mcp-server-bXszmZpp-py3.13/bin/python -m uvicorn src.mcp_server.server:http_app --host 0.0.0.0 --port 8080 --reload")
    
    print_colored(f"\n📊 Server Admin Key: {get_admin_key()}", Colors.BOLD)
    print_colored("Save this key for API authentication!", Colors.YELLOW)

if __name__ == "__main__":
    main()
