#!/usr/bin/env python3
"""Test script to verify all modules import correctly and optional dependencies are handled."""

def test_ai_tools():
    """Test AI tools with optional dependencies."""
    print("Testing AI tools...")
    try:
        from src.mcp_server.tools.ai_tools import create_embeddings, vector_search
        print("✅ AI tools imported successfully")
        
        # Test optional dependency handling
        result = create_embeddings(['test'], 'sentence-transformers/all-MiniLM-L6-v2')
        assert result["status"] == "error", "Should fail without sentence-transformers"
        assert "sentence_transformers not installed" in result["error"]
        print("✅ Optional dependency handling works correctly")
        
        return True
    except Exception as e:
        print(f"❌ AI tools test failed: {e}")
        return False

def test_server_imports():
    """Test server module imports."""
    print("Testing server imports...")
    try:
        from src.mcp_server.server import http_app, mcp_server
        from src.mcp_server.admin import admin_router
        print("✅ Server modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Server import test failed: {e}")
        return False

def test_core_tools():
    """Test core development tools."""
    print("Testing core tools...")
    try:
        from src.mcp_server.tools import run_code, lint_code, format_code, test_code
        print("✅ Core tools imported successfully")
        return True
    except Exception as e:
        print(f"❌ Core tools test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running import and functionality tests...\n")
    
    tests = [
        test_ai_tools,
        test_server_imports,
        test_core_tools
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Server is ready to use.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
