# GitHub Copilot Instructions for Python MCP Server

You are an expert Python developer working on a Model Context Protocol (MCP) server. This codebase follows specific patterns and conventions that you should always adhere to.

## Project Context
- **Framework**: Python MCP server using mcp-python library
- **Purpose**: Safe Python code execution with development tools (linting, formatting, testing, docs)
- **Architecture**: MCP JSON-RPC protocol + HTTP REST API bridge
- **Cloud**: AWS, GCP, Azure SDK integrations
- **Tools**: ruff (linting), black (formatting), pytest (testing), subprocess (execution)

## Code Patterns to Follow

### Tool Function Structure
```python
def tool_name(param: str) -> Dict[str, Any]:
    """
    Tool description for MCP.
    
    Args:
        param: Parameter description
        
    Returns:
        Dict with status, result/error, traceback
    """
    try:
        # Validate inputs
        if not param:
            raise ValueError("param is required")
            
        # Perform operation
        result = execute_operation(param)
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }
```

### Subprocess Pattern
```python
result = subprocess.run(
    [command, *args],
    capture_output=True,
    text=True,
    timeout=30,
    check=False
)
return {
    "stdout": result.stdout,
    "stderr": result.stderr, 
    "returncode": result.returncode
}
```

### HTTP Endpoint Pattern
```python
@http_app.post("/endpoint")
async def http_endpoint(request: Request):
    data = await request.json()
    param = data.get("param", "")
    result = tool_function(param)
    return JSONResponse(content=result)
```

### Test Pattern
```python
def test_function():
    result = function("input")
    assert result["status"] == "success"
    assert "result" in result
```

## Security Rules
- NEVER use eval(), exec(), or compile() on user input
- ALWAYS use subprocess for code execution
- ALWAYS implement timeouts (default 30s)
- ALWAYS validate inputs
- ALWAYS use temporary files for file operations
- ALWAYS clean up resources

## Response Format
All tool functions must return:
```python
{
    "status": "success|error",
    "result": {...},        # on success
    "error": "...",         # on error
    "traceback": "..."      # on error
}
```

## Cloud SDK Patterns
- AWS: Use boto3 with proper error handling
- GCP: Use google-cloud-* libraries
- Azure: Use azure-* libraries
- Always handle ClientError and similar exceptions

## Import Conventions
```python
import subprocess
import tempfile
import traceback
from typing import Dict, Any
from mcp_server.types import MCPResponse
from mcp_server.config import DEFAULTS
```

## When Adding Features
1. Create tool function following patterns
2. Add to server.py (MCP registration + HTTP endpoint)
3. Add comprehensive tests
4. Update documentation
5. Follow error handling patterns

## Performance Guidelines
- Timeout all operations (30s default)
- Limit output size (5000 chars)
- Use temp files for safety
- Clean up resources properly

Always prioritize security, follow established patterns, and maintain consistency with existing code.
