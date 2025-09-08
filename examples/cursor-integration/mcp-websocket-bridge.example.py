#!/usr/bin/env python3
"""
Simple WebSocket bridge for Cursor MCP connection
Replace YOUR_K8S_IP and YOUR_PORT with your Kubernetes service details
"""
import asyncio
import websockets
import json
import sys
from typing import Any, Dict

async def websocket_bridge():
    """Bridge stdio to WebSocket MCP server"""
    # REPLACE WITH YOUR KUBERNETES SERVICE IP:PORT
    uri = "ws://YOUR_K8S_IP:YOUR_PORT/mcp"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🎉 Connected to Python MCP Server!", file=sys.stderr)
            
            async def read_stdin():
                """Read from stdin and send to WebSocket"""
                while True:
                    try:
                        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                        if not line:
                            break
                        await websocket.send(line.strip())
                    except Exception as e:
                        print(f"Error reading stdin: {e}", file=sys.stderr)
                        break
            
            async def read_websocket():
                """Read from WebSocket and write to stdout"""
                async for message in websocket:
                    print(message, flush=True)
            
            # Run both directions concurrently
            await asyncio.gather(read_stdin(), read_websocket())
            
    except Exception as e:
        print(f"❌ Connection failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(websocket_bridge())
