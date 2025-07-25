#!/usr/bin/env python3
"""
Quick test and demo script for the Python MCP Server.
"""

from mcp_server.tools.run_code import run_python

def test_basic_functionality():
    """Test basic tool functionality."""
    print("🧪 Testing Python code execution...")
    
    test_code = """
print("Hello from MCP Python execution!")
result = 2 + 2
print(f"2 + 2 = {result}")
"""
    
    result = run_python(test_code)
    
    if "error" not in result and result.get("returncode", 1) == 0:
        print("✅ Code execution successful!")
        print(f"Output: {result.get('stdout', 'No output')}")
        return True
    else:
        print("❌ Code execution failed!")
        print(f"Error: {result.get('error', result.get('stderr', 'Unknown error'))}")
        return False

def main():
    """Run basic tests and show server info."""
    print("🚀 Python MCP Server - Quick Test\n")
    
    # Test basic functionality
    success = test_basic_functionality()
    
    if success:
        print("""
✅ All tests passed!

🌟 Your Python MCP Server is ready to use!

To start the full server:
  poetry run python -m mcp_server.server

Available tools:
  • Python code execution (run_python_tool)
  • Code linting (lint_python_tool)  
  • Code formatting (format_python_tool)
  • AI/LLM integration (ai_chat_tool)
  • Cloud SDK tools (AWS, GCP, Azure)
  • System intelligence tools
  • And much more!

API Documentation:
  HTTP: http://localhost:8080/docs (when server is running)
""")
    else:
        print("❌ Basic tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()
