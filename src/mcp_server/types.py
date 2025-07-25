"""
Type definitions and schemas for the Python MCP Server.

This module provides type hints and data models that help GitHub Copilot
understand the expected data structures and function signatures throughout
the codebase.
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

# Common response types
MCPResponse = Dict[str, Any]
ToolResult = Dict[str, Union[str, int, bool, None]]

class Status(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

@dataclass
class CodeExecutionResult:
    """Result from Python code execution."""
    stdout: str
    stderr: str
    returncode: int
    execution_time: Optional[float] = None
    
@dataclass
class LintResult:
    """Result from code linting."""
    issues: List[Dict[str, Any]]
    is_clean: bool
    total_issues: int
    
@dataclass
class FormatResult:
    """Result from code formatting."""
    formatted_code: str
    changed: bool
    diff: Optional[str] = None
    
@dataclass
class TestResult:
    """Result from test execution."""
    passed: int
    failed: int
    errors: int
    output: str
    test_file_created: bool
    
@dataclass
class DocGenResult:
    """Result from documentation generation."""
    docstrings_added: int
    files_processed: int
    documentation_created: bool
    
@dataclass
class CloudOperationResult:
    """Result from cloud SDK operations."""
    operation: str
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None

# HTTP request/response schemas
@dataclass
class CodeRequest:
    """HTTP request schema for code-related operations."""
    code: str
    language: str = "python"
    
@dataclass
class TestRequest:
    """HTTP request schema for test operations."""
    code: str
    test_type: str = "unit"
    coverage: bool = False
    
@dataclass
class CloudRequest:
    """HTTP request schema for cloud operations."""
    operation: str
    parameters: Dict[str, Any]
    provider: str  # aws, gcp, azure
    
# MCP tool function type
MCPTool = callable[[...], MCPResponse]

# Common error response structure
def error_response(error: str, traceback: Optional[str] = None) -> MCPResponse:
    """Standard error response format."""
    return {
        "status": Status.ERROR.value,
        "error": error,
        "traceback": traceback
    }

def success_response(result: Any) -> MCPResponse:
    """Standard success response format."""
    return {
        "status": Status.SUCCESS.value,
        "result": result
    }
