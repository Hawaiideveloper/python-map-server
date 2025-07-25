# GitHub Copilot Context for Python MCP Server

## Project Overview
This is a Python MCP (Model Context Protocol) Server that provides safe Python code execution, automated testing, linting, formatting, documentation generation, and cloud SDK integrations.

## Architecture Patterns
- **MCP Protocol**: Uses mcp-python library for JSON-RPC communication over stdin/stdout
- **Tool Registration**: All tools are registered with the MCP server using `app.register_tool()`
- **HTTP Bridge**: FastAPI provides REST endpoints for non-MCP clients
- **Sandboxing**: Python code execution uses subprocess with tempfiles for safety
- **Cloud Integrations**: AWS (boto3), GCP (google-cloud-storage), Azure (azure-storage-blob)

## Code Patterns and Conventions

### Tool Function Signature
```python
def tool_name(param: str) -> dict:
    """
    Tool description for MCP protocol.
    
    Args:
        param: Parameter description
        
    Returns:
        dict: {"status": "success/error", "result": ..., "error": ...}
    """
```

### Error Handling Pattern
```python
try:
    # Tool logic here
    return {"status": "success", "result": result}
except Exception as e:
    return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
```

### Subprocess Execution Pattern
```python
result = subprocess.run(
    [command, *args],
    capture_output=True,
    text=True,
    timeout=30,
    cwd=working_dir
)
return {
    "stdout": result.stdout,
    "stderr": result.stderr,
    "returncode": result.returncode
}
```

### HTTP Endpoint Pattern
```python
@http_app.post("/endpoint_name")
async def http_endpoint_name(request: Request):
    data = await request.json()
    param = data.get("param", "")
    result = tool_function(param)
    return JSONResponse(content=result)
```

## Security Considerations
- Always use subprocess for code execution, never exec() or eval()
- Use tempfiles with proper cleanup
- Implement timeouts for all subprocess calls
- Validate inputs before processing
- Use bandit for security scanning

## Testing Patterns
- Use pytest for all tests
- Mock subprocess calls in tests
- Test both success and error cases
- Test timeout scenarios
- Test security boundaries

## Dependencies
- mcp-python: Core MCP protocol implementation
- fastapi: HTTP API server
- ruff: Fast Python linter
- black: Code formatter
- pytest: Testing framework
- boto3, google-cloud-storage, azure-storage-blob: Cloud SDKs

## Common Operations
- Tool registration: `app.register_tool(function)`
- HTTP endpoint registration: `@http_app.post("/path")`
- Safe code execution: Use subprocess with tempfile
- Error responses: Always include error and traceback fields
