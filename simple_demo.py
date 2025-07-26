#!/usr/bin/env python3
"""
Simple MCP Server Test - Bypass authentication issues for local testing
"""

import requests
import json

def test_local_server():
    """Test the local server with various endpoints."""
    base_url = "http://localhost:8080"
    admin_key = "mcp_admin_7kuF6ve-SdAvQ5joKObch4tGSdmIMifCA6CPFGuCa-k"
    
    print("🧪 Testing Local MCP Server")
    print("=" * 40)
    
    # Test endpoints that don't require auth
    print("\n1. Testing public endpoints...")
    
    # Health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.status_code} - {response.json()['status']}")
    except Exception as e:
        print(f"❌ Health failed: {e}")
    
    # Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        data = response.json()
        print(f"✅ Root: {response.status_code} - {data['service']}")
        print(f"   Available endpoints: {len(data['endpoints'])}")
    except Exception as e:
        print(f"❌ Root failed: {e}")
    
    # Documentation endpoint
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"✅ Docs: {response.status_code} - Swagger UI available")
    except Exception as e:
        print(f"❌ Docs failed: {e}")
    
    print("\n2. Testing authenticated endpoints...")
    headers = {
        "Content-Type": "application/json",
        "X-Admin-Key": admin_key
    }
    
    # Test code execution
    test_code = "print('Hello from local MCP server!')
import sys
print(f'Python: {sys.version.split()[0]}')"
    try:
        response = requests.post(
            f"{base_url}/run_code",
            headers=headers,
            json={"code": test_code, "timeout": 10}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Code execution: {response.status_code}")
            if result.get("result", {}).get("stdout"):
                print(f"   Output: {result['result']['stdout'].strip()}")
        else:
            print(f"⚠️  Code execution: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Code execution failed: {e}")
    
    # Test linting
    bad_code = "print( 'badly formatted code' )"
    try:
        response = requests.post(
            f"{base_url}/lint_code",
            headers=headers,
            json={"code": bad_code}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Code linting: {response.status_code}")
            issues = result.get("result", {}).get("issues", [])
            print(f"   Found {len(issues)} linting issues")
        else:
            print(f"⚠️  Code linting: {response.status_code}")
    except Exception as e:
        print(f"❌ Code linting failed: {e}")
    
    print("
3. Direct curl examples for testing:")
    print(f"# Test code execution:")
    print(f"""curl -X POST {base_url}/run_code 
  -H "Content-Type: application/json" 
  -H "X-Admin-Key: {admin_key}" 
  -d '{{"code": "print("Hello World!")"}}' | jq""")
    
    print(f"
# Test system info:")
    print(f"""curl -H "X-Admin-Key: {admin_key}" {base_url}/system/info | jq""")
    
    print(f"
# Test linting:")
    print(f"""curl -X POST {base_url}/lint_code 
  -H "Content-Type: application/json" 
  -H "X-Admin-Key: {admin_key}" 
  -d '{{"code": "print( "test" )"}}' | jq""")

if __name__ == "__main__":
    test_local_server()

def get_api_key():
    """Get API key from user input."""
    print("\n🔑 You need an API key to use the server.")
    print("When you started the server, it showed you keys like:")
    print("   Admin Key: mcp_admin_ABC123...")
    print("   User Key: mcp_user_XYZ789...")
    
    api_key = input("\n📝 Please paste your User Key here: ").strip()
    
    if not api_key.startswith("mcp_"):
        print("⚠️  That doesn't look like a valid API key.")
        print("   It should start with 'mcp_user_' or 'mcp_admin_'")
        return None
    
    return api_key

def make_request(endpoint, data, api_key):
    """Make a request to the server."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}{endpoint}", 
                               headers=headers, 
                               json=data, 
                               timeout=30)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def demo_run_code(api_key):
    """Demo: Run some Python code."""
    print("\n🏃‍♂️ Demo 1: Running Python Code")
    print("=" * 40)
    
    code = "print('Hello from your MCP Server!')\nprint('2 + 2 =', 2 + 2)"
    print(f"Running this code: {code}")
    
    response = make_request("/run_code", {"code": code}, api_key)
    
    if response and response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Output:")
        print(result.get("stdout", ""))
        if result.get("stderr"):
            print(f"Warnings: {result['stderr']}")
    else:
        print(f"❌ Failed: {response.status_code if response else 'No response'}")
        if response:
            print(f"Error: {response.text}")

def demo_lint_code(api_key):
    """Demo: Check code quality."""
    print("\n🔍 Demo 2: Checking Code Quality")
    print("=" * 40)
    
    messy_code = "def hello( ):print( 'hi' )  # This is messy!"
    print(f"Checking this messy code: {messy_code}")
    
    response = make_request("/lint_code", {"code": messy_code}, api_key)
    
    if response and response.status_code == 200:
        result = response.json()
        print(f"✅ Lint check complete!")
        print(f"Return code: {result.get('returncode', 'unknown')}")
        if result.get('lint_output'):
            print(f"Issues found: {result['lint_output']}")
        else:
            print("No issues found!")
    else:
        print(f"❌ Failed: {response.status_code if response else 'No response'}")

def demo_format_code(api_key):
    """Demo: Format messy code."""
    print("\n✨ Demo 3: Formatting Code")
    print("=" * 40)
    
    messy_code = "def hello():print('hi')"
    print(f"Original messy code: {messy_code}")
    
    response = make_request("/format_code", {"code": messy_code}, api_key)
    
    if response and response.status_code == 200:
        result = response.json()
        print(f"✅ Code formatted!")
        print(f"Pretty code:")
        print(result.get("formatted_code", ""))
    else:
        print(f"❌ Failed: {response.status_code if response else 'No response'}")

def demo_math_calculation(api_key):
    """Demo: Do some math calculations."""
    print("\n🧮 Demo 4: Math Calculations")
    print("=" * 40)
    
    math_code = """
import math

# Calculate some interesting numbers
print("π (pi) =", math.pi)
print("Square root of 16 =", math.sqrt(16))
print("2 to the power of 8 =", 2**8)

# Some list operations
numbers = [1, 2, 3, 4, 5]
print("Sum of", numbers, "=", sum(numbers))
print("Average =", sum(numbers) / len(numbers))
"""
    
    print("Running some math calculations...")
    
    response = make_request("/run_code", {"code": math_code}, api_key)
    
    if response and response.status_code == 200:
        result = response.json()
        print(f"✅ Math calculations complete!")
        print(result.get("stdout", ""))
    else:
        print(f"❌ Failed: {response.status_code if response else 'No response'}")

def demo_error_handling(api_key):
    """Demo: See how errors are handled."""
    print("\n🚨 Demo 5: Error Handling")
    print("=" * 40)
    
    bad_code = "print('This will work')\nprint(1 / 0)  # This will cause an error!"
    print("Running code that has an error...")
    
    response = make_request("/run_code", {"code": bad_code}, api_key)
    
    if response and response.status_code == 200:
        result = response.json()
        print(f"✅ Request completed (even with error in code)!")
        print(f"Output: {result.get('stdout', '')}")
        if result.get('stderr'):
            print(f"Error output: {result['stderr']}")
        print(f"Return code: {result.get('returncode', 'unknown')}")
    else:
        print(f"❌ Failed: {response.status_code if response else 'No response'}")

def main():
    """Run all the demos."""
    print("🚀 Welcome to your MCP Server Demo!")
    print("=" * 50)
    print("This will test your server with simple examples.")
    print("Make sure your server is running first!")
    
    # Check if server is running
    if not test_server():
        return
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return
    
    print(f"\n🎉 Great! Let's run some demos...")
    
    # Run demos
    demo_run_code(api_key)
    demo_lint_code(api_key)
    demo_format_code(api_key)
    demo_math_calculation(api_key)
    demo_error_handling(api_key)
    
    print("\n🎉 All demos complete!")
    print("\n💡 Next steps:")
    print("1. Try modifying the code in this script")
    print("2. Look at the QUICKSTART.md file for more examples")
    print("3. Start building your own applications!")
    
    print("\n🔗 Useful endpoints to try:")
    print("- POST /run_code - Run Python code")
    print("- POST /lint_code - Check code quality") 
    print("- POST /format_code - Format code")
    print("- POST /test_code - Generate and run tests")
    print("- POST /generate_docs - Add documentation")

if __name__ == "__main__":
    main()
