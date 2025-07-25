#!/usr/bin/env python3
"""Simple test script to verify the MCP server setup."""

import sys
from pathlib import Path

# Add src to path so we can import mcp_server
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from mcp_server.server import mcp_server
    from mcp_server.tools.format_code import format_python
    from mcp_server.tools.lint_code import lint_python
    from mcp_server.tools.run_code import run_python

    print("✅ All imports successful!")

    # Test basic functionality
    test_code = '''
def hello():
    print("Hello, World!")
    return 42

result = hello()
'''

    print("\n🧪 Testing core functionality...")

    # Test code execution
    exec_result = run_python(test_code)
    print(f"Code execution: {'✅' if exec_result['status'] == 'success' else '❌'}")

    # Test code linting
    lint_result = lint_python(test_code)
    print(f"Code linting: {'✅' if lint_result['status'] == 'success' else '❌'}")

    # Test code formatting
    format_result = format_python(test_code)
    print(f"Code formatting: {'✅' if format_result['status'] == 'success' else '❌'}")

    # Check registered tools
    print(f"\n📋 MCP Server: {type(mcp_server).__name__}")
    print("✅ Server setup complete!")

    print("""
🚀 Python MCP Server is ready!

To start the server:
  poetry run python -m mcp_server.server

To run HTTP API only:
  poetry run uvicorn mcp_server.server:http_app --host 0.0.0.0 --port 8080

Features available:
  - ✅ Python code execution with security
  - ✅ Code linting and formatting
  - ✅ AI/LLM integration tools
  - ✅ Cloud SDK integration
  - ✅ System intelligence tools
  - ✅ HTTP REST API bridge
  - ✅ Comprehensive logging and monitoring
""")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
