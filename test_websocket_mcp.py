#!/usr/bin/env python3
"""
Test MCP WebSocket functionality with a real WebSocket client.
"""

import asyncio
import json
import ssl
import websockets

async def test_mcp_websocket():
    """Test the deployed MCP WebSocket server."""
    uri = "wss://python-mcp-server-production.up.railway.app/mcp"
    
    print("🔗 Testing MCP WebSocket Connection")
    print("=" * 50)
    print(f"Connecting to: {uri}")
    
    try:
        # Connect to WebSocket with SSL context
        ssl_context = ssl.create_default_context()
        
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print("✅ WebSocket connection established")
            
            # Test 1: Initialize
            print("\n1. Sending initialize request...")
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "1.0",
                    "capabilities": {}
                },
                "id": 1
            }
            
            await websocket.send(json.dumps(init_request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if result.get("result"):
                print(f"✅ Initialize successful: {result['result']['serverInfo']['name']}")
            else:
                print(f"❌ Initialize failed: {result}")
                return False
            
            # Test 2: List tools
            print("\n2. Requesting tools list...")
            tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            
            await websocket.send(json.dumps(tools_request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if result.get("result") and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"✅ Tools list received: {len(tools)} tools available")
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"   - {tool['name']}: {tool['description']}")
            else:
                print(f"❌ Tools list failed: {result}")
                return False
            
            # Test 3: Call a tool
            print("\n3. Calling run_code tool...")
            call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "run_code",
                    "arguments": {
                        "code": "print('Hello from WebSocket MCP!')\nresult = 2 + 2\nprint(f'2 + 2 = {result}')"
                    }
                },
                "id": 3
            }
            
            await websocket.send(json.dumps(call_request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if result.get("result"):
                print("✅ Tool execution successful:")
                content = result["result"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    for item in content:
                        if item.get("type") == "text":
                            print(f"   Output: {item['text'][:100]}..." if len(item['text']) > 100 else f"   Output: {item['text']}")
                else:
                    print(f"   Result: {content}")
            else:
                print(f"❌ Tool call failed: {result}")
                return False
            
            print("\n" + "=" * 50)
            print("🎉 MCP WebSocket Test Complete!")
            print("✅ All WebSocket MCP functionality is working correctly")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

async def test_fallback_without_websockets():
    """Fallback test using basic socket if websockets module not available."""
    print("⚠️  websockets module not available")
    print("🔄 Testing MCP protocol logic instead...")
    
    # Use our mock test
    from test_mcp_protocol import test_mcp_protocol
    await test_mcp_protocol()
    
    print("\n📝 To test the actual WebSocket connection:")
    print("1. Install websockets: pip install websockets")
    print("2. Run this script again")
    print("3. Or use a WebSocket client like wscat:")
    print("   wscat -c wss://python-mcp-server-production.up.railway.app/mcp")

if __name__ == "__main__":
    try:
        asyncio.run(test_mcp_websocket())
    except ImportError:
        asyncio.run(test_fallback_without_websockets())
