#!/usr/bin/env python3
"""
Simple MCP Server Test - Test the local server functionality
"""

import requests
import json

def test_local_server():
    """Test the local server with various endpoints."""
    base_url = "http://localhost:8080"
    admin_key = "mcp_admin_7kuF6ve-SdAvQ5joKObch4tGSdmIMifCA6CPFGuCa-k"
    
    print("🧪 Testing Local MCP Server")
    print("=" * 40)
    
    # Test public endpoints
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
    
    print("\n2. Testing authenticated endpoints...")
    headers = {
        "Content-Type": "application/json",
        "X-Admin-Key": admin_key
    }
    
    # Test code execution
    test_code = "print('Hello from local MCP server!')\nimport sys\nprint(f'Python: {sys.version.split()[0]}')"
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
    
    print("\n3. Example curl commands for testing:")
    print(f"# Test code execution:")
    print(f"""curl -X POST {base_url}/run_code \\
  -H "Content-Type: application/json" \\
  -H "X-Admin-Key: {admin_key}" \\
  -d '{{"code": "print(\\"Hello World!\\")"}}' """)
    
    print(f"\n# Test system info:")
    print(f"""curl -H "X-Admin-Key: {admin_key}" {base_url}/system/info""")

if __name__ == "__main__":
    test_local_server()
