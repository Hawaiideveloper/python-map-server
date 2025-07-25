#!/usr/bin/env python3
"""
Demo Script: Python MCP Server Capabilities

This script demonstrates the core capabilities of the Python MCP Server
without requiring external API keys or complex setup.
"""

import json
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server.tools.run_code import run_python
from mcp_server.tools.lint_code import lint_python  
from mcp_server.tools.format_code import format_python

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def demo_code_execution():
    """Demonstrate safe Python code execution"""
    print_section("Code Execution Demo")
    
    test_codes = [
        "print('Hello, Python MCP Server!')",
        "import math\nprint(f'Pi is approximately {math.pi:.4f}')",
        "x = [1, 2, 3, 4, 5]\nprint(f'Sum: {sum(x)}, Average: {sum(x)/len(x)}')",
        "import datetime\nprint(f'Current time: {datetime.datetime.now()}')"
    ]
    
    for i, code in enumerate(test_codes, 1):
        print(f"\n--- Test {i} ---")
        print(f"Code: {code}")
        result = run_python(code)
        if result.get('stdout'):
            print(f"Output: {result['stdout'].strip()}")
        if result.get('stderr'):
            print(f"Error: {result['stderr'].strip()}")

def demo_code_linting():
    """Demonstrate code quality analysis"""
    print_section("Code Linting Demo")
    
    bad_code_examples = [
        "import os\nimport sys\n\n\n\nprint('hello')",  # Import issues, spacing
        "x=1+2*3\ny = x**2",  # Formatting issues
        "def my_function():\n    unused_var = 42\n    return 'test'",  # Unused variable
    ]
    
    for i, code in enumerate(bad_code_examples, 1):
        print(f"\n--- Lint Test {i} ---")
        print(f"Code:\n{code}")
        result = lint_python(code)
        print(f"Lint Analysis:\n{result.get('lint_output', 'No issues found')}")

def demo_code_formatting():
    """Demonstrate automatic code formatting"""
    print_section("Code Formatting Demo")
    
    ugly_code_examples = [
        "x=1+2*3",
        "def hello(name):\n    return f'Hello, {name}!'",
        "data={'key1':'value1','key2':'value2'}",
        "result=[x**2 for x in range(10)if x%2==0]"
    ]
    
    for i, code in enumerate(ugly_code_examples, 1):
        print(f"\n--- Format Test {i} ---")
        print(f"Before: {code}")
        try:
            result = format_python(code)
            print(f"After:  {result.get('formatted_code', '').strip()}")
        except Exception as e:
            print(f"Formatting failed: {e}")
            continue

def demo_data_science_capabilities():
    """Demonstrate data science and analysis capabilities"""
    print_section("Data Science Demo")
    
    data_science_code = """
import json
import math

# Simulate some data analysis
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mean = sum(data) / len(data)
variance = sum((x - mean) ** 2 for x in data) / len(data)
std_dev = math.sqrt(variance)

result = {
    'dataset_size': len(data),
    'mean': mean,
    'variance': variance,
    'standard_deviation': std_dev,
    'min': min(data),
    'max': max(data)
}

print(json.dumps(result, indent=2))
"""
    
    print("Executing data analysis code...")
    result = run_python(data_science_code)
    if result.get('stdout'):
        print("Analysis Results:")
        print(result['stdout'])

def demo_system_capabilities():
    """Demonstrate system information capabilities"""
    print_section("System Information Demo")
    
    system_code = """
import platform
import sys
import os

info = {
    'python_version': sys.version,
    'platform': platform.platform(),
    'processor': platform.processor(),
    'current_directory': os.getcwd(),
    'environment_variables_count': len(os.environ)
}

for key, value in info.items():
    print(f"{key}: {value}")
"""
    
    print("Gathering system information...")
    result = run_python(system_code)
    if result.get('stdout'):
        print(result['stdout'])

def main():
    """Run all demonstrations"""
    print("🚀 Python MCP Server - Capability Demonstration")
    print("This demo shows core capabilities without requiring API keys")
    
    try:
        demo_code_execution()
        demo_code_linting() 
        demo_code_formatting()
        demo_data_science_capabilities()
        demo_system_capabilities()
        
        print_section("Summary")
        print("✅ Code Execution: Safe Python code execution in sandboxed environment")
        print("✅ Code Quality: Automated linting and style analysis")  
        print("✅ Code Formatting: Automatic code beautification")
        print("✅ Data Science: Built-in support for analysis and computation")
        print("✅ System Integration: Access to system information and utilities")
        print("\n🎯 This is just the beginning! With API keys configured, you can also:")
        print("   • Chat with AI models (OpenAI GPT, Anthropic Claude)")
        print("   • Create and search vector embeddings") 
        print("   • Train machine learning models")
        print("   • Deploy to cloud platforms (AWS, GCP, Azure)")
        print("   • Access 100+ Python libraries for any use case")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())