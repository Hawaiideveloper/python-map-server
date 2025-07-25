# GitHub Copilot Instructions for Python MCP Server

You are an expert Python developer working on a Model Context Protocol (MCP) server. This codebase follows specific patterns and conventions that you should always adhere to.

## Project Context
- **Framework**: Python MCP server using mcp-python library
- **Package Manager**: Poetry for dependency management and virtual environments
- **Purpose**: Safe Python code execution with development tools (linting, formatting, testing, docs)
- **Architecture**: MCP JSON-RPC protocol + HTTP REST API bridge
- **Cloud**: AWS, GCP, Azure SDK integrations
- **Tools**: ruff (linting), black (formatting), pytest (testing), subprocess (execution)
- **Enhanced Features**: Security sandboxing, logging, authentication, admin dashboard

## Code Patterns to Follow

### Enhanced Tool Function Structure
```python
from mcp_server.utils.logging import log_tool_execution
from mcp_server.utils.security import validate_code_safety

@log_tool_execution("tool_name")
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
            
        # Security validation (for code tools)
        if "code" in locals():
            safety_check = validate_code_safety(code)
            if not safety_check["is_safe"]:
                raise SecurityError(safety_check["reason"])
            
        # Perform operation
        result = execute_operation(param)
        
        return {
            "status": "success",
            "result": result,
            "metadata": {
                "tool": "tool_name",
                "execution_time": time.time() - start_time
            }
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "tool_name"
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

### Enhanced HTTP Endpoint Pattern
```python
from mcp_server.utils.auth import check_rate_limit, authenticate_request
from mcp_server.utils.logging import log_http_request

@http_app.post("/endpoint")
@log_http_request("endpoint")
async def http_endpoint(
    request: Request,
    auth_info: Dict[str, Any] = Depends(authenticate_request)
):
    # Rate limiting
    check_rate_limit(request)
    
    data = await request.json()
    param = data.get("param", "")
    
    # Call tool function
    result = tool_function(param)
    
    # Add rate limit headers
    rate_info = rate_limiter.get_rate_limit_info(get_client_id(request))
    headers = {
        "X-RateLimit-Limit": str(rate_info["limit"]),
        "X-RateLimit-Remaining": str(rate_info["remaining"])
    }
    
    status_code = 200 if result["status"] == "success" else 400
    return JSONResponse(content=result, headers=headers, status_code=status_code)
```

### Enhanced Test Pattern
```python
import pytest
from unittest.mock import patch, Mock
from mcp_server.tools import tool_module

class TestToolName:
    def test_successful_execution(self):
        result = tool_module.tool_function("valid_input")
        assert result["status"] == "success"
        assert "result" in result
        assert result["metadata"]["tool"] == "tool_name"
        
    def test_invalid_input(self):
        result = tool_module.tool_function("")
        assert result["status"] == "error"
        assert "required" in result["error"]
        
    @patch('subprocess.run')
    def test_subprocess_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        result = tool_module.tool_function("input")
        assert result["status"] == "error"
        assert "timeout" in result["error"].lower()
        
    @pytest.mark.asyncio
    async def test_http_endpoint(self, test_client):
        response = await test_client.post("/endpoint", json={"param": "test"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
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
from typing import Dict, Any, Optional
from mcp_server.types import MCPResponse
from mcp_server.config import DEFAULTS
from mcp_server.utils.logging import log_tool_execution
from mcp_server.utils.security import execute_code_securely
```

## Poetry Workflow
- **Install dependencies**: `poetry install`
- **Add new dependency**: `poetry add package-name`
- **Add dev dependency**: `poetry add --group dev package-name`
- **Run server**: `poetry run mcp-server` or `poetry run python -m mcp_server.server`
- **Run tests**: `poetry run pytest`
- **Lint code**: `poetry run ruff check .`
- **Format code**: `poetry run black .`
- **Activate shell**: `poetry shell`

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

## Development Workflow with Poetry
1. **Setup environment**: `poetry install`
2. **Add dependencies**: `poetry add package-name`
3. **Run development server**: `poetry run python -m mcp_server.server`
4. **Run tests**: `poetry run pytest -v`
5. **Code quality checks**:
   - `poetry run ruff check .` (linting)
   - `poetry run black .` (formatting)
   - `poetry run pytest --cov=src` (coverage)
6. **Build package**: `poetry build`

## Configuration Management
- All settings in `src/mcp_server/config.py`
- Environment variables via `.env` file
- Tool configurations in `pyproject.toml`
- Database settings in `src/mcp_server/utils/database.py`

## Security Best Practices
- Use `execute_code_securely()` for code execution
- Implement `validate_code_safety()` before execution
- Apply rate limiting with `@check_rate_limit`
- Authenticate requests with `@authenticate_request`
- Log security events with `log_security_event()`

Always prioritize security, follow established patterns, and maintain consistency with existing code.
