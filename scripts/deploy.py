#!/usr/bin/env python3
"""
Deployment script for Python MCP Server
Handles both Kubernetes and Docker deployments with fallback logic
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

def run_command(cmd: list, timeout: int = 60, check: bool = True) -> Dict[str, Any]:
    """Run a command and return structured output"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "error": f"Command timed out after {timeout}s",
            "stdout": e.stdout or "",
            "stderr": e.stderr or ""
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Command failed with exit code {e.returncode}",
            "stdout": e.stdout or "",
            "stderr": e.stderr or "",
            "returncode": e.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": ""
        }

def check_kubernetes_connection() -> bool:
    """Check if we can connect to Kubernetes cluster"""
    print("🔍 Checking Kubernetes connection...")
    result = run_command(["kubectl", "cluster-info"], timeout=10, check=False)
    
    if result["success"]:
        print("✅ Kubernetes cluster is accessible")
        return True
    else:
        print("❌ Cannot connect to Kubernetes cluster")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return False

def check_docker_connection() -> bool:
    """Check if Docker daemon is available"""
    print("🔍 Checking Docker connection...")
    result = run_command(["docker", "info"], timeout=10, check=False)
    
    if result["success"]:
        print("✅ Docker daemon is accessible")
        return True
    else:
        print("❌ Cannot connect to Docker daemon")
        return False

def deploy_to_kubernetes() -> bool:
    """Deploy to Kubernetes using existing k8s scripts"""
    print("🚀 Deploying to Kubernetes...")
    
    # Use the existing approved commands script
    env = os.environ.copy()
    env["SKIP_LOCAL_BUILD"] = "1"
    
    result = run_command([
        "./.vscode/approved-commands.sh", "deploy"
    ], timeout=300, check=False)
    
    if result["success"]:
        print("✅ Kubernetes deployment successful")
        return True
    else:
        print("❌ Kubernetes deployment failed")
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Stderr: {result['stderr']}")
        return False

def build_and_run_docker() -> bool:
    """Build and run Docker container locally"""
    print("🐳 Building and running Docker container...")
    
    # Build the image
    print("Building Docker image...")
    result = run_command([
        "docker", "build", "-t", "python-mcp-server:latest", "."
    ], timeout=300)
    
    if not result["success"]:
        print("❌ Docker build failed")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return False
    
    print("✅ Docker image built successfully")
    
    # Stop any existing container
    run_command([
        "docker", "stop", "python-mcp-server"
    ], check=False)
    
    run_command([
        "docker", "rm", "python-mcp-server"
    ], check=False)
    
    # Run the container
    print("Starting Docker container...")
    result = run_command([
        "docker", "run", "-d",
        "--name", "python-mcp-server",
        "-p", "8080:8080",
        "-p", "3030:3030",
        "--env-file", ".env",
        "python-mcp-server:latest"
    ])
    
    if result["success"]:
        print("✅ Docker container started successfully")
        print("🌐 Server available at:")
        print("  - HTTP API: http://localhost:8080")
        print("  - MCP WebSocket: ws://localhost:3030/mcp")
        return True
    else:
        print("❌ Failed to start Docker container")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return False

def test_deployment() -> bool:
    """Test if the deployment is working"""
    print("🧪 Testing deployment...")
    
    # Wait a moment for the service to start
    time.sleep(5)
    
    # Try to reach the health endpoint
    try:
        import requests
        response = requests.get("http://localhost:8080/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except ImportError:
        # Use curl if requests is not available
        result = run_command([
            "curl", "-f", "-s", "http://localhost:8080/health"
        ], timeout=10, check=False)
        
        if result["success"]:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Python MCP Server Deployment Script")
    print("=" * 50)
    
    # Check environment
    if not Path(".env").exists():
        print("⚠️  .env file not found. Please create one from .env.example")
        return 1
    
    # Try Kubernetes first
    if check_kubernetes_connection():
        if deploy_to_kubernetes():
            if test_deployment():
                print("\n🎉 Kubernetes deployment successful!")
                return 0
            else:
                print("\n❌ Kubernetes deployment tests failed")
        else:
            print("\n❌ Kubernetes deployment failed")
    
    # Fallback to Docker
    print("\n🔄 Falling back to Docker deployment...")
    if check_docker_connection():
        if build_and_run_docker():
            if test_deployment():
                print("\n🎉 Docker deployment successful!")
                return 0
            else:
                print("\n❌ Docker deployment tests failed")
        else:
            print("\n❌ Docker deployment failed")
    else:
        print("\n❌ Neither Kubernetes nor Docker is available")
        return 1
    
    print("\n❌ All deployment methods failed")
    return 1

if __name__ == "__main__":
    sys.exit(main())
