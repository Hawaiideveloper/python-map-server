#!/usr/bin/env python3
"""
HTTP API Usage Examples

This script demonstrates how to interact with the Python MCP Server via HTTP API.
Note: This requires the server to be running on localhost:8080
"""

import requests
import json
import time

def test_api_endpoint(endpoint, data, description):
    """Test an API endpoint and display results"""
    print(f"\n🧪 Testing: {description}")
    print(f"Endpoint: POST {endpoint}")
    print(f"Payload: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(f"http://localhost:8080{endpoint}", 
                               json=data, 
                               timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: poetry run python -m mcp_server.server")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Test various API endpoints"""
    print("🚀 Python MCP Server - HTTP API Examples")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "endpoint": "/run_code",
            "data": {"code": "print('Hello from HTTP API!')"},
            "description": "Basic Code Execution"
        },
        {
            "endpoint": "/run_code", 
            "data": {"code": "import math\nresult = math.sqrt(16)\nprint(f'Square root of 16 is {result}')"},
            "description": "Math Calculation"
        },
        {
            "endpoint": "/lint_code",
            "data": {"code": "import os\n\n\nprint('test')"},
            "description": "Code Linting"
        },
        {
            "endpoint": "/format_code",
            "data": {"code": "x=1+2*3\ny=x**2"},
            "description": "Code Formatting"
        },
        {
            "endpoint": "/run_code",
            "data": {"code": """
import json
data = {'name': 'Python MCP Server', 'version': '0.3.0', 'features': ['AI', 'ML', 'Cloud']}
print(json.dumps(data, indent=2))
"""},
            "description": "JSON Data Processing"
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        success = test_api_endpoint(**test_case)
        if success:
            success_count += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n📊 Results: {success_count}/{len(test_cases)} tests passed")
    
    if success_count == 0:
        print("\n💡 To start the server:")
        print("   cd /path/to/python-mcp-server")
        print("   poetry run python -m mcp_server.server")
        print("   # The server will run on http://localhost:8080")
    
    print("\n🔗 Available API Endpoints:")
    endpoints = [
        "/run_code - Execute Python code",
        "/lint_code - Analyze code quality", 
        "/format_code - Format code with Black",
        "/test_code - Run tests with pytest",
        "/doc_gen - Generate documentation",
        "/ai/chat - Chat with AI models (requires API keys)",
        "/ai/embeddings - Create text embeddings",
        "/ai/vector_search - Search vector databases",
        "/system/info - Get system information",
        "/sdk/aws_* - AWS operations",
        "/sdk/gcp_* - Google Cloud operations", 
        "/sdk/azure_* - Azure operations"
    ]
    
    for endpoint in endpoints:
        print(f"   • {endpoint}")

if __name__ == "__main__":
    main()