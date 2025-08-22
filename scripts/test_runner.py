#!/usr/bin/env python3
"""
Unit Test Runner for Python MCP Server
Runs tests one by one with detailed reporting and failure tracking
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "test_results": []
        }
        
    def run_command(self, cmd: list, timeout: int = 60) -> Dict[str, Any]:
        """Run a command and return structured output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "error": f"Test timed out after {timeout}s",
                "stdout": e.stdout or "",
                "stderr": e.stderr or ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    def discover_test_files(self) -> List[Path]:
        """Discover all test files in the tests directory"""
        test_dir = Path("tests")
        if not test_dir.exists():
            print("❌ Tests directory not found")
            return []
        
        test_files = []
        for file_path in test_dir.rglob("test_*.py"):
            if file_path.is_file():
                test_files.append(file_path)
        
        # Also check for pytest-style test files
        for file_path in test_dir.rglob("*_test.py"):
            if file_path.is_file() and file_path not in test_files:
                test_files.append(file_path)
        
        return sorted(test_files)
    
    def run_single_test_file(self, test_file: Path) -> Dict[str, Any]:
        """Run a single test file and return results"""
        print(f"\n🧪 Running {test_file}")
        print("-" * 50)
        
        start_time = time.time()
        
        # Run pytest on the specific file with verbose output
        cmd = [
            "python", "-m", "pytest", 
            str(test_file), 
            "-v", 
            "--tb=short",
            "--no-header",
            "--json-report",
            "--json-report-file=/tmp/pytest_report.json"
        ]
        
        result = self.run_command(cmd, timeout=120)
        duration = time.time() - start_time
        
        # Try to parse pytest JSON report
        test_details = []
        try:
            if Path("/tmp/pytest_report.json").exists():
                with open("/tmp/pytest_report.json", "r") as f:
                    pytest_data = json.load(f)
                    test_details = pytest_data.get("tests", [])
        except Exception as e:
            print(f"⚠️  Could not parse test report: {e}")
        
        test_result = {
            "file": str(test_file),
            "success": result["success"],
            "duration": duration,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "test_details": test_details
        }
        
        if result["success"]:
            print(f"✅ {test_file} PASSED ({duration:.2f}s)")
            self.results["passed"] += 1
        else:
            print(f"❌ {test_file} FAILED ({duration:.2f}s)")
            print(f"Error output:\n{result['stderr']}")
            self.results["failed"] += 1
        
        return test_result
    
    def run_all_tests(self) -> bool:
        """Run all discovered test files"""
        print("🧪 Python MCP Server Test Runner")
        print("=" * 50)
        
        # Check if pytest is available
        pytest_check = self.run_command(["python", "-m", "pytest", "--version"])
        if not pytest_check["success"]:
            print("❌ pytest not found. Installing...")
            install_result = self.run_command(["pip", "install", "pytest", "pytest-json-report"])
            if not install_result["success"]:
                print("❌ Failed to install pytest")
                return False
        
        test_files = self.discover_test_files()
        if not test_files:
            print("❌ No test files found")
            return False
        
        print(f"📋 Found {len(test_files)} test files:")
        for test_file in test_files:
            print(f"  - {test_file}")
        
        self.results["total_tests"] = len(test_files)
        
        # Run each test file individually
        for test_file in test_files:
            test_result = self.run_single_test_file(test_file)
            self.results["test_results"].append(test_result)
        
        return self.generate_report()
    
    def generate_report(self) -> bool:
        """Generate and save test report"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        print(f"Total test files: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']} ✅")
        print(f"Failed: {self.results['failed']} ❌")
        
        if self.results["failed"] > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results["test_results"]:
                if not result["success"]:
                    print(f"  - {result['file']}")
        
        # Save detailed report
        report_file = Path("test_results.json")
        try:
            with open(report_file, "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"\n📝 Detailed report saved to {report_file}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")
        
        success = self.results["failed"] == 0
        if success:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n❌ {self.results['failed']} test file(s) failed")
        
        return success
    
    def run_specific_test(self, test_pattern: str) -> bool:
        """Run tests matching a specific pattern"""
        print(f"🧪 Running tests matching pattern: {test_pattern}")
        
        cmd = [
            "python", "-m", "pytest", 
            "-k", test_pattern,
            "-v", 
            "--tb=short"
        ]
        
        result = self.run_command(cmd, timeout=120)
        
        if result["success"]:
            print("✅ Tests passed")
            return True
        else:
            print("❌ Tests failed")
            print(f"Output:\n{result['stdout']}")
            print(f"Error:\n{result['stderr']}")
            return False

def main():
    """Main test runner function"""
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        # Run specific test pattern
        test_pattern = sys.argv[1]
        success = runner.run_specific_test(test_pattern)
    else:
        # Run all tests
        success = runner.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
