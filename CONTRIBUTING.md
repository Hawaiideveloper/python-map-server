# Contributing to Python MCP Server

This guide provides detailed patterns and conventions that GitHub Copilot can learn from to generate better code suggestions.

## Code Style and Patterns

### Function Documentation
All functions must include comprehensive docstrings following this pattern:

```python
def tool_function(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Brief description of what the function does.
    
    This function performs [specific operation] and returns [result type].
    Used in MCP protocol as tool [tool_name].
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter with default value
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - result: The actual result data (on success)
            - error: Error message (on error)
            - traceback: Full traceback (on error)
            
    Raises:
        ValueError: When invalid parameters are provided
        TimeoutError: When operation exceeds time limit
        
    Example:
        >>> result = tool_function("example", 20)
        >>> assert result["status"] == "success"
    """
```

### Error Handling Pattern
All tools must follow this error handling pattern:

```python
def tool_function(param: str) -> Dict[str, Any]:
    """Tool function with proper error handling."""
    try:
        # Validate inputs
        if not param or not isinstance(param, str):
            raise ValueError("param must be a non-empty string")
            
        # Perform the operation
        result = perform_operation(param)
        
        # Return success response
        return {
            "status": "success",
            "result": result,
            "metadata": {
                "execution_time": time.time() - start_time,
                "param_length": len(param)
            }
        }
        
    except ValueError as e:
        return {
            "status": "error",
            "error": f"Validation error: {str(e)}",
            "traceback": traceback.format_exc()
        }
    except TimeoutError as e:
        return {
            "status": "error", 
            "error": f"Operation timed out: {str(e)}",
            "traceback": traceback.format_exc()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "traceback": traceback.format_exc()
        }
```

### Subprocess Execution Pattern
For tools that execute external commands:

```python
def execute_external_tool(command: List[str], input_data: str = "", timeout: int = 30) -> Dict[str, Any]:
    """Execute external tool with proper error handling."""
    try:
        result = subprocess.run(
            command,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # Don't raise on non-zero exit
        )
        
        return {
            "status": "success",
            "result": {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(command)
            }
        }
        
    except subprocess.TimeoutExpired as e:
        return {
            "status": "error",
            "error": f"Command timed out after {timeout}s: {' '.join(command)}",
            "traceback": traceback.format_exc()
        }
    except FileNotFoundError as e:
        return {
            "status": "error",
            "error": f"Command not found: {command[0]}",
            "traceback": traceback.format_exc()
        }
```

### File Operations Pattern
For tools that work with files:

```python
def process_file_safely(file_path: str, operation: str) -> Dict[str, Any]:
    """Process file with proper cleanup and error handling."""
    temp_file = None
    try:
        # Create temporary file for safe operations
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(content)
            temp_file.flush()
            
            # Perform operation on temp file
            result = perform_file_operation(temp_file.name, operation)
            
            return {
                "status": "success",
                "result": result,
                "file_processed": temp_file.name
            }
            
    except PermissionError as e:
        return {
            "status": "error",
            "error": f"Permission denied: {str(e)}",
            "traceback": traceback.format_exc()
        }
    except IOError as e:
        return {
            "status": "error",
            "error": f"File I/O error: {str(e)}",
            "traceback": traceback.format_exc()
        }
    finally:
        # Always cleanup temporary files
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass  # Best effort cleanup
```

### HTTP Endpoint Pattern
For HTTP API endpoints:

```python
@http_app.post("/tool_endpoint")
async def http_tool_endpoint(request: Request) -> JSONResponse:
    """
    HTTP endpoint for tool_name.
    
    Expected JSON body:
        {
            "param1": "value1",
            "param2": "value2"
        }
    
    Returns:
        JSONResponse with tool result
    """
    try:
        # Parse request data
        data = await request.json()
        
        # Extract parameters with validation
        param1 = data.get("param1")
        if not param1:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error": "Missing required parameter: param1"
                }
            )
        
        param2 = data.get("param2", "default_value")
        
        # Call the actual tool function
        result = tool_function(param1, param2)
        
        # Return appropriate HTTP status
        status_code = 200 if result["status"] == "success" else 400
        return JSONResponse(status_code=status_code, content=result)
        
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": "Invalid JSON in request body"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": f"Internal server error: {str(e)}",
                "traceback": traceback.format_exc()
            }
        )
```

### Test Pattern
For comprehensive test coverage:

```python
class TestToolName:
    """Test class for tool_name function."""
    
    def test_successful_operation(self):
        """Test successful tool execution."""
        result = tool_name("valid_input")
        
        assert result["status"] == "success"
        assert "result" in result
        assert result["result"] is not None
        
    def test_invalid_input(self):
        """Test tool with invalid input."""
        result = tool_name("")
        
        assert result["status"] == "error"
        assert "error" in result
        assert "validation" in result["error"].lower()
        
    def test_edge_cases(self):
        """Test tool with edge cases."""
        # Test with None
        result = tool_name(None)
        assert result["status"] == "error"
        
        # Test with very long input
        long_input = "x" * 10000
        result = tool_name(long_input)
        # Should either succeed or fail gracefully
        assert result["status"] in ["success", "error"]
        
    @patch('subprocess.run')
    def test_subprocess_failure(self, mock_run):
        """Test handling of subprocess failures."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        
        result = tool_name("input")
        
        assert result["status"] == "error"
        assert "timeout" in result["error"].lower()
        
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test asynchronous operations if applicable."""
        result = await async_tool_name("input")
        
        assert result["status"] == "success"
```

### Cloud SDK Pattern
For cloud provider integrations:

```python
def cloud_operation(provider: str, operation: str, **kwargs) -> Dict[str, Any]:
    """
    Generic cloud operation with provider-specific handling.
    
    Args:
        provider: Cloud provider ("aws", "gcp", "azure")
        operation: Operation to perform
        **kwargs: Provider-specific parameters
    """
    try:
        # Validate provider
        if provider not in ["aws", "gcp", "azure"]:
            raise ValueError(f"Unsupported provider: {provider}")
            
        # Get provider-specific handler
        handler = {
            "aws": handle_aws_operation,
            "gcp": handle_gcp_operation, 
            "azure": handle_azure_operation
        }[provider]
        
        # Execute operation
        result = handler(operation, **kwargs)
        
        return {
            "status": "success",
            "result": result,
            "provider": provider,
            "operation": operation
        }
        
    except ClientError as e:
        # AWS specific error
        return {
            "status": "error",
            "error": f"AWS error: {str(e)}",
            "error_code": e.response['Error']['Code']
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Cloud operation failed: {str(e)}",
            "provider": provider,
            "operation": operation
        }
```

## Adding New Tools

### 1. Create Tool Function
Create a new file in `src/mcp_server/tools/` following the patterns above.

### 2. Register with MCP Server
Add to `src/mcp_server/server.py`:

```python
from mcp_server.tools import new_tool
app.register_tool(new_tool.function_name)
```

### 3. Add HTTP Endpoint
Add to `src/mcp_server/server.py`:

```python
@http_app.post("/new_tool")
async def http_new_tool(request: Request):
    data = await request.json()
    result = new_tool.function_name(data.get("param"))
    return JSONResponse(content=result)
```

### 4. Add Tests
Create tests in `tests/test_new_tool.py` following the test patterns.

### 5. Update Documentation
Add examples to `docs/examples.md` and update README.md.

## Code Quality Requirements

### Type Hints
All functions must have complete type hints:

```python
from typing import Dict, Any, Optional, List, Union

def function_name(
    param1: str,
    param2: Optional[int] = None,
    param3: List[str] = None
) -> Dict[str, Any]:
    """Function with complete type hints."""
    if param3 is None:
        param3 = []
    # ... implementation
```

### Security Considerations
- Never use `eval()`, `exec()`, or `compile()` on user input
- Always use subprocess for code execution
- Implement timeouts for all operations
- Validate all inputs
- Use temporary files for file operations
- Clean up resources in finally blocks

### Performance Guidelines
- Set reasonable timeouts (default 30s)
- Limit output size to prevent memory issues
- Use streaming for large data when possible
- Implement proper error handling for resource exhaustion

## Git Workflow

1. Create feature branch: `git checkout -b feature/new-tool`
2. Implement following patterns above
3. Add comprehensive tests
4. Run quality checks: `ruff check`, `black --check`, `pytest`
5. Update documentation
6. Create pull request with detailed description

This pattern-rich documentation helps GitHub Copilot understand the project's conventions and generate consistent, high-quality code suggestions.
