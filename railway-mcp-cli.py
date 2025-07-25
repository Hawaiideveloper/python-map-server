#!/usr/bin/env python3
"""
Advanced Railway MCP Server CLI
Provides comprehensive control over the deployed MCP server
"""

import argparse
import json
import requests
import sys
import subprocess
import time
from typing import Dict, Any, Optional
import asyncio
import websockets
import ssl

class RailwayMCPCLI:
    def __init__(self):
        self.base_url = "https://python-mcp-server-production.up.railway.app"
        self.admin_key = "mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs"
        self.headers = {"X-Admin-Key": self.admin_key, "Content-Type": "application/json"}
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to the MCP server."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {}
            }
        except Exception as e:
            return {"status_code": 500, "error": str(e)}

    def status(self) -> None:
        """Check server health and status."""
        print("🔍 Checking MCP Server Status...")
        
        result = self._make_request("GET", "/health")
        if result["status_code"] == 200:
            data = result["data"]
            print(f"✅ Server Status: {data['status']}")
            print(f"📦 Version: {data['version']}")
            print(f"⏱️  Uptime: {data.get('uptime', 'Unknown')}")
            print(f"🌐 Environment: {data.get('environment', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    def info(self) -> None:
        """Get detailed server information."""
        print("📋 Server Information:")
        
        result = self._make_request("GET", "/")
        if result["status_code"] == 200:
            data = result["data"]
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed to get server info: {result.get('error', 'Unknown error')}")

    def execute_code(self, code: str, timeout: int = 30) -> None:
        """Execute Python code on the server."""
        print(f"⚡ Executing Python code (timeout: {timeout}s)...")
        
        result = self._make_request("POST", "/run_code", {"code": code, "timeout": timeout})
        if result["status_code"] == 200:
            data = result["data"]
            if data["status"] == "success":
                print("✅ Execution successful:")
                if data["result"]["stdout"]:
                    print(f"📤 stdout:\n{data['result']['stdout']}")
                if data["result"]["stderr"]:
                    print(f"⚠️  stderr:\n{data['result']['stderr']}")
                print(f"🔢 Return code: {data['result']['returncode']}")
            else:
                print(f"❌ Execution failed: {data['error']}")
        else:
            print(f"❌ Request failed: {result.get('error', 'Unknown error')}")

    def lint_code(self, code: str) -> None:
        """Lint Python code."""
        print("🔍 Linting Python code...")
        
        result = self._make_request("POST", "/lint_code", {"code": code})
        if result["status_code"] == 200:
            data = result["data"]
            if data["status"] == "success":
                issues = data["result"]["issues"]
                if not issues:
                    print("✅ No linting issues found!")
                else:
                    print(f"⚠️  Found {len(issues)} linting issues:")
                    for issue in issues:
                        print(f"  Line {issue['line']}: {issue['message']}")
            else:
                print(f"❌ Linting failed: {data['error']}")
        else:
            print(f"❌ Request failed: {result.get('error', 'Unknown error')}")

    def system_info(self) -> None:
        """Get system information."""
        print("🖥️  System Information:")
        
        result = self._make_request("GET", "/system/info")
        if result["status_code"] == 200:
            data = result["data"]
            if data["status"] == "success":
                info = data["result"]
                print(f"💾 CPU: {info['cpu']['cpu_count']} cores ({info['cpu']['cpu_percent']:.1f}% usage)")
                print(f"🧠 Memory: {info['memory']['total_gb']:.1f}GB total ({info['memory']['percent']:.1f}% used)")
                print(f"💿 Disk: {info['disk']['total_gb']:.1f}GB total ({info['disk']['percent']:.1f}% used)")
                print(f"🐍 Python: {info['python']['version']}")
                print(f"📦 Packages: {len(info['python']['packages'])} installed")
            else:
                print(f"❌ Failed to get system info: {data['error']}")
        else:
            print(f"❌ Request failed: {result.get('error', 'Unknown error')}")

    async def test_websocket_mcp(self) -> None:
        """Test WebSocket MCP connection."""
        print("🔗 Testing WebSocket MCP Connection...")
        
        uri = f"wss://{self.base_url.replace('https://', '')}/mcp"
        print(f"Connecting to: {uri}")
        
        try:
            ssl_context = ssl.create_default_context()
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                print("✅ WebSocket connected")
                
                # Test initialize
                init_request = {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {"protocolVersion": "1.0", "capabilities": {}},
                    "id": 1
                }
                
                await websocket.send(json.dumps(init_request))
                response = await websocket.recv()
                result = json.loads(response)
                
                if result.get("result"):
                    print(f"✅ Initialize successful: {result['result']['serverInfo']['name']}")
                    
                    # Test tools list
                    tools_request = {
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "params": {},
                        "id": 2
                    }
                    
                    await websocket.send(json.dumps(tools_request))
                    response = await websocket.recv()
                    result = json.loads(response)
                    
                    if result.get("result"):
                        tools = result["result"]["tools"]
                        print(f"✅ Found {len(tools)} MCP tools")
                        for tool in tools[:5]:  # Show first 5
                            print(f"  - {tool['name']}: {tool['description']}")
                    else:
                        print(f"❌ Tools list failed: {result}")
                else:
                    print(f"❌ Initialize failed: {result}")
                    
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")

    def trigger_deployment(self) -> None:
        """Trigger a new deployment via git."""
        print("🚀 Triggering new deployment...")
        
        try:
            # Create deployment trigger
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            with open("deployment_trigger.txt", "w") as f:
                f.write(f"Deployment triggered at: {timestamp}\n")
            
            subprocess.run(["git", "add", "deployment_trigger.txt"], check=True)
            subprocess.run(["git", "commit", "-m", f"Trigger deployment - {timestamp}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            
            print("✅ Deployment triggered successfully")
            print("🔄 Railway will automatically deploy the changes")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to trigger deployment: {e}")

    def interactive_mode(self) -> None:
        """Start interactive mode for continuous operations."""
        print("🔧 MCP Server Interactive Mode")
        print("Type 'help' for commands, 'exit' to quit")
        
        while True:
            try:
                command = input("\nmcp> ").strip()
                
                if command == "exit":
                    print("👋 Goodbye!")
                    break
                elif command == "help":
                    print("Available commands:")
                    print("  status      - Check server status")
                    print("  info        - Get server information")
                    print("  system      - Get system information")
                    print("  exec <code> - Execute Python code")
                    print("  lint <code> - Lint Python code")
                    print("  ws-test     - Test WebSocket MCP")
                    print("  deploy      - Trigger deployment")
                    print("  exit        - Quit interactive mode")
                elif command == "status":
                    self.status()
                elif command == "info":
                    self.info()
                elif command == "system":
                    self.system_info()
                elif command.startswith("exec "):
                    code = command[5:]
                    self.execute_code(code)
                elif command.startswith("lint "):
                    code = command[5:]
                    self.lint_code(code)
                elif command == "ws-test":
                    asyncio.run(self.test_websocket_mcp())
                elif command == "deploy":
                    self.trigger_deployment()
                else:
                    print(f"Unknown command: {command}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Railway MCP Server CLI")
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("--code", help="Python code to execute")
    parser.add_argument("--file", help="File to process")
    parser.add_argument("--timeout", type=int, default=30, help="Execution timeout")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    
    args = parser.parse_args()
    
    cli = RailwayMCPCLI()
    
    if args.interactive:
        cli.interactive_mode()
        return
    
    if not args.command:
        print("Usage: python railway-mcp-cli.py <command> [options]")
        print("Commands: status, info, system, exec, lint, ws-test, deploy")
        print("Use --interactive for interactive mode")
        return
    
    if args.command == "status":
        cli.status()
    elif args.command == "info":
        cli.info()
    elif args.command == "system":
        cli.system_info()
    elif args.command == "exec":
        if args.code:
            cli.execute_code(args.code, args.timeout)
        elif args.file:
            with open(args.file, 'r') as f:
                cli.execute_code(f.read(), args.timeout)
        else:
            print("Error: --code or --file required for exec command")
    elif args.command == "lint":
        if args.code:
            cli.lint_code(args.code)
        elif args.file:
            with open(args.file, 'r') as f:
                cli.lint_code(f.read())
        else:
            print("Error: --code or --file required for lint command")
    elif args.command == "ws-test":
        asyncio.run(cli.test_websocket_mcp())
    elif args.command == "deploy":
        cli.trigger_deployment()
    else:
        print(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
