"""
WebSocket MCP Server implementation for true MCP protocol support.

This module provides WebSocket transport for the MCP protocol, allowing
true MCP clients (like Claude Desktop) to connect while maintaining
the HTTP bridge for web clients.
"""

import asyncio
import json
import logging
from typing import Any, Dict

import websockets
from fastapi import WebSocket, WebSocketDisconnect
from mcp.server.fastmcp.server import FastMCP

from mcp_server.utils.logging import setup_logger

logger = setup_logger("mcp_websocket")


class MCPWebSocketHandler:
    """WebSocket handler for MCP JSON-RPC protocol."""
    
    def __init__(self, mcp_server: FastMCP):
        self.mcp_server = mcp_server
        self.active_connections: set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New MCP WebSocket connection established. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        self.active_connections.discard(websocket)
        logger.info(f"MCP WebSocket connection closed. Remaining: {len(self.active_connections)}")
    
    async def handle_mcp_message(self, websocket: WebSocket, message: str) -> None:
        """Process MCP JSON-RPC message and send response."""
        try:
            # Parse JSON-RPC request
            request = json.loads(message)
            logger.debug(f"Received MCP request: {request.get('method', 'unknown')}")
            
            # Validate JSON-RPC format
            if not self._is_valid_jsonrpc(request):
                error_response = self._create_error_response(
                    request.get('id'), 
                    -32600, 
                    "Invalid Request"
                )
                await websocket.send_text(json.dumps(error_response))
                return
            
            # Handle different MCP methods
            response = await self._process_mcp_request(request)
            
            # Send response
            if response:
                await websocket.send_text(json.dumps(response))
                logger.debug(f"Sent MCP response for: {request.get('method', 'unknown')}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in MCP message: {e}")
            error_response = self._create_error_response(None, -32700, "Parse error")
            await websocket.send_text(json.dumps(error_response))
            
        except Exception as e:
            logger.error(f"Error processing MCP message: {e}")
            error_response = self._create_error_response(
                request.get('id') if 'request' in locals() else None,
                -32603,
                f"Internal error: {str(e)}"
            )
            await websocket.send_text(json.dumps(error_response))
    
    async def _process_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP request and return response."""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        try:
            if method == 'initialize':
                return await self._handle_initialize(request_id, params)
            
            elif method == 'tools/list':
                return await self._handle_tools_list(request_id)
            
            elif method == 'tools/call':
                return await self._handle_tool_call(request_id, params)
            
            elif method == 'notifications/initialized':
                # Notification - no response needed
                logger.info("MCP client initialized")
                return None
            
            else:
                return self._create_error_response(
                    request_id, 
                    -32601, 
                    f"Method not found: {method}"
                )
                
        except Exception as e:
            logger.error(f"Error in MCP method {method}: {e}")
            return self._create_error_response(
                request_id,
                -32603,
                f"Internal error: {str(e)}"
            )
    
    async def _handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        logger.info(f"MCP initialization request: {params}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "logging": {},
                    "prompts": {
                        "listChanged": False
                    },
                    "resources": {
                        "subscribe": False,
                        "listChanged": False
                    }
                },
                "serverInfo": {
                    "name": "python-mcp-server",
                    "version": "0.3.0"
                },
                "instructions": "A comprehensive Python MCP server with AI/LLM integration, code execution, and development tools."
            }
        }
    
    async def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request."""
        # Get tools from FastMCP server
        tools = []
        
        # Convert FastMCP tools to MCP format
        for tool_name, tool_info in self.mcp_server._tools.items():
            tool_schema = {
                "name": tool_name,
                "description": tool_info.get("description", f"Execute {tool_name}"),
                "inputSchema": {
                    "type": "object",
                    "properties": tool_info.get("parameters", {}),
                    "required": tool_info.get("required", [])
                }
            }
            tools.append(tool_schema)
        
        logger.info(f"Listing {len(tools)} MCP tools")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_tool_call(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if not tool_name:
            return self._create_error_response(
                request_id, 
                -32602, 
                "Missing tool name"
            )
        
        logger.info(f"MCP tool call: {tool_name}")
        
        try:
            # Execute tool through FastMCP
            if tool_name in self.mcp_server._tools:
                tool_func = self.mcp_server._tools[tool_name]["function"]
                
                # Call the tool function
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**arguments)
                else:
                    result = tool_func(**arguments)
                
                # Format response
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            else:
                return self._create_error_response(
                    request_id,
                    -32601,
                    f"Tool not found: {tool_name}"
                )
                
        except Exception as e:
            logger.error(f"Tool execution error for {tool_name}: {e}")
            return self._create_error_response(
                request_id,
                -32603,
                f"Tool execution failed: {str(e)}"
            )
    
    def _is_valid_jsonrpc(self, request: Dict[str, Any]) -> bool:
        """Validate JSON-RPC 2.0 format."""
        return (
            isinstance(request, dict) and
            request.get('jsonrpc') == '2.0' and
            'method' in request and
            isinstance(request['method'], str)
        )
    
    def _create_error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }


# Global WebSocket handler instance
websocket_handler = None


def get_websocket_handler(mcp_server: FastMCP) -> MCPWebSocketHandler:
    """Get or create WebSocket handler instance."""
    global websocket_handler
    if websocket_handler is None:
        websocket_handler = MCPWebSocketHandler(mcp_server)
    return websocket_handler
