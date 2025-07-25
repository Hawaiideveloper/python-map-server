#!/usr/bin/env python3
"""
Test Railway deployment and WebSocket MCP functionality.
"""
import json
import time
import subprocess
import requests

def test_deployment():
    """Test the Railway deployment and check for WebSocket support."""
    base_url = "https://python-mcp-server-production.up.railway.app"
    admin_key = "mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs"
    headers = {"X-Admin-Key": admin_key}
    
    print("🚀 Testing Railway Deployment")
    print("=" * 50)
    
    # Test 1: Basic health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']} - Version: {data.get('version', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Check for WebSocket support in root endpoint
    print("\n2. Testing for WebSocket protocol support...")
    try:
        response = requests.get(f"{base_url}/", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'protocols' in data:
                print("✅ WebSocket protocols found:")
                for protocol in data['protocols']:
                    print(f"   - {protocol['name']}: {protocol['url']}")
                return True
            else:
                print("⚠️  No 'protocols' field found - WebSocket support not yet deployed")
                print("Current response:", json.dumps(data, indent=2))
                return False
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def trigger_redeploy():
    """Try to trigger a Railway redeploy using git webhook."""
    print("\n3. Checking git webhook trigger...")
    
    # Create a small change to trigger redeploy
    try:
        # Add a timestamp to trigger rebuild
        with open("deployment_trigger.txt", "w") as f:
            f.write(f"Deployment triggered at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        subprocess.run(["git", "add", "deployment_trigger.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "Trigger deployment for WebSocket support"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Git push successful - Railway should auto-deploy")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False

def wait_for_deployment(max_wait=300):
    """Wait for deployment to complete and check for WebSocket support."""
    print(f"\n4. Waiting for deployment (max {max_wait}s)...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if test_deployment():
            print(f"🎉 WebSocket deployment successful after {time.time() - start_time:.0f}s")
            return True
        
        print(f"⏳ Still waiting... ({time.time() - start_time:.0f}s)")
        time.sleep(30)
    
    print(f"⚠️  Timeout after {max_wait}s - WebSocket support may not be deployed yet")
    return False

if __name__ == "__main__":
    print("🔄 Railway WebSocket Deployment Test")
    print("=" * 60)
    
    # First test current state
    if test_deployment():
        print("🎉 WebSocket support already deployed!")
    else:
        print("📦 WebSocket support not found - triggering redeploy...")
        if trigger_redeploy():
            wait_for_deployment()
        else:
            print("❌ Could not trigger redeploy")
