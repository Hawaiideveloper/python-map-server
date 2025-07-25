#!/usr/bin/env python3
"""
Quick Start Test Script for Python Code Quality CI/CD

This script helps you test the Python MCP server quality analysis
on your local repository before setting up CI/CD.

Usage:
    python quick-test.py [path_to_your_repo]

If no path is provided, it will analyze the current directory.
"""

import sys
import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

def main():
    """Main test function"""
    print("🚀 Python Code Quality Quick Test")
    print("=" * 50)
    
    # Determine repository path
    if len(sys.argv) > 1:
        repo_path = Path(sys.argv[1]).resolve()
    else:
        repo_path = Path.cwd()
    
    if not repo_path.exists():
        print(f"❌ Error: Path {repo_path} does not exist")
        sys.exit(1)
    
    print(f"📁 Analyzing: {repo_path}")
    
    # Check if it's a Python repository
    if not is_python_repo(repo_path):
        print("⚠️  Warning: No Python files found in this directory")
        print("   This tool is designed for Python repositories")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Setup and run analysis
    try:
        setup_environment()
        run_quick_analysis(repo_path)
        cleanup()
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        cleanup()
        sys.exit(1)

def is_python_repo(repo_path: Path) -> bool:
    """Check if directory contains Python files"""
    python_files = list(repo_path.rglob("*.py"))
    return len(python_files) > 0

def setup_environment():
    """Setup the test environment"""
    print("\n🔧 Setting up test environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor} detected")
    
    # Check for required tools
    tools_status = check_tools()
    if not tools_status["has_required"]:
        print("⚠️  Some tools are missing, using simplified analysis")

def check_tools() -> Dict[str, Any]:
    """Check for available analysis tools"""
    tools = {
        "ruff": check_command("ruff --version"),
        "mypy": check_command("mypy --version"),
        "pytest": check_command("pytest --version"),
        "coverage": check_command("coverage --version"),
        "bandit": check_command("bandit --version"),
    }
    
    available = sum(1 for available in tools.values() if available)
    total = len(tools)
    
    print(f"📊 Available tools: {available}/{total}")
    for tool, available in tools.items():
        status = "✅" if available else "❌"
        print(f"   {status} {tool}")
    
    return {
        "tools": tools,
        "has_required": tools["ruff"] or available >= 2,
        "available_count": available
    }

def check_command(command: str) -> bool:
    """Check if a command is available"""
    try:
        subprocess.run(
            command.split(),
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False

def run_quick_analysis(repo_path: Path):
    """Run a quick analysis of the repository"""
    print(f"\n🔍 Analyzing {repo_path.name}...")
    
    # Initialize results
    results = {
        "repository": str(repo_path),
        "python_files": 0,
        "total_lines": 0,
        "lint_issues": 0,
        "test_files": 0,
        "has_setup": False,
        "has_requirements": False,
        "has_readme": False,
        "analysis_summary": []
    }
    
    # Collect basic info
    collect_basic_info(repo_path, results)
    
    # Run available analyses
    run_lint_check(repo_path, results)
    run_structure_check(repo_path, results)
    run_test_check(repo_path, results)
    
    # Generate report
    generate_quick_report(results)

def collect_basic_info(repo_path: Path, results: Dict[str, Any]):
    """Collect basic repository information"""
    print("📊 Collecting repository information...")
    
    # Count Python files and lines
    python_files = []
    total_lines = 0
    
    for py_file in repo_path.rglob("*.py"):
        if should_exclude_file(py_file):
            continue
            
        try:
            lines = len(py_file.read_text(encoding='utf-8', errors='ignore').splitlines())
            python_files.append(py_file)
            total_lines += lines
        except Exception:
            continue
    
    results["python_files"] = len(python_files)
    results["total_lines"] = total_lines
    
    # Check for important files
    results["has_setup"] = any(
        (repo_path / name).exists() 
        for name in ["setup.py", "pyproject.toml", "setup.cfg"]
    )
    
    results["has_requirements"] = any(
        (repo_path / name).exists() 
        for name in ["requirements.txt", "Pipfile", "poetry.lock", "pyproject.toml"]
    )
    
    results["has_readme"] = any(
        (repo_path / name).exists() 
        for name in ["README.md", "README.rst", "README.txt", "readme.md"]
    )
    
    print(f"   📄 Python files: {results['python_files']}")
    print(f"   📏 Lines of code: {results['total_lines']:,}")

def run_lint_check(repo_path: Path, results: Dict[str, Any]):
    """Run linting analysis"""
    print("🐛 Checking code style...")
    
    try:
        # Try ruff first
        result = subprocess.run(
            ["ruff", "check", str(repo_path), "--quiet"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )
        
        if result.returncode in [0, 1]:
            # Count issues from output
            issues = result.stdout.count('\n') if result.stdout else 0
            results["lint_issues"] = issues
            
            if issues == 0:
                results["analysis_summary"].append("✅ No linting issues found")
            else:
                results["analysis_summary"].append(f"⚠️  {issues} linting issues found")
                
            return
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Fallback: simple pattern checking
    print("   Using simplified lint check...")
    issues = run_simple_lint_check(repo_path)
    results["lint_issues"] = issues
    
    if issues == 0:
        results["analysis_summary"].append("✅ Basic style check passed")
    else:
        results["analysis_summary"].append(f"⚠️  ~{issues} potential style issues")

def run_simple_lint_check(repo_path: Path) -> int:
    """Simple lint checking without external tools"""
    issues = 0
    
    for py_file in repo_path.rglob("*.py"):
        if should_exclude_file(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Check line length
                if len(line) > 100:
                    issues += 1
                
                # Check for common issues
                if line.strip().endswith(',') and i < len(lines) and not lines[i].strip():
                    issues += 1  # Trailing comma followed by blank line
                
                # Basic import organization
                if line.startswith('from ') and 'import *' in line:
                    issues += 1  # Star imports
                    
        except Exception:
            continue
            
        if issues > 50:  # Limit for performance
            break
    
    return min(issues, 99)

def run_structure_check(repo_path: Path, results: Dict[str, Any]):
    """Check repository structure"""
    print("🏗️  Checking project structure...")
    
    structure_score = 0
    
    # Check for important files
    if results["has_setup"]:
        structure_score += 1
        results["analysis_summary"].append("✅ Package configuration found")
    else:
        results["analysis_summary"].append("⚠️  No setup.py or pyproject.toml found")
    
    if results["has_requirements"]:
        structure_score += 1
        results["analysis_summary"].append("✅ Dependencies specification found")
    
    if results["has_readme"]:
        structure_score += 1
        results["analysis_summary"].append("✅ README file found")
    
    # Check for common directories
    common_dirs = ["src", "tests", "test", "docs", "examples"]
    found_dirs = [d for d in common_dirs if (repo_path / d).exists()]
    
    if found_dirs:
        structure_score += 1
        results["analysis_summary"].append(f"✅ Standard directories: {', '.join(found_dirs)}")
    
    # Check for __init__.py files
    init_files = list(repo_path.rglob("__init__.py"))
    if init_files:
        results["analysis_summary"].append(f"✅ Package structure ({len(init_files)} packages)")
    
    results["structure_score"] = structure_score

def run_test_check(repo_path: Path, results: Dict[str, Any]):
    """Check for tests"""
    print("🧪 Checking tests...")
    
    # Look for test files
    test_patterns = [
        "test_*.py",
        "*_test.py",
        "tests/*.py",
        "test/*.py"
    ]
    
    test_files = set()
    for pattern in test_patterns:
        test_files.update(repo_path.rglob(pattern))
    
    # Filter out __pycache__ etc.
    test_files = [f for f in test_files if not should_exclude_file(f)]
    
    results["test_files"] = len(test_files)
    
    if test_files:
        results["analysis_summary"].append(f"✅ {len(test_files)} test files found")
        
        # Try to run tests quickly
        if check_command("pytest --version"):
            print("   Running quick test check...")
            try:
                result = subprocess.run(
                    ["pytest", str(repo_path), "--collect-only", "-q"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    check=False
                )
                
                if "collected" in result.stdout:
                    test_count = result.stdout.count("::test_")
                    if test_count > 0:
                        results["analysis_summary"].append(f"✅ ~{test_count} tests detected")
                        
            except subprocess.TimeoutExpired:
                results["analysis_summary"].append("⚠️  Test discovery timed out")
            except Exception:
                pass
    else:
        results["analysis_summary"].append("⚠️  No test files found")

def generate_quick_report(results: Dict[str, Any]):
    """Generate and display the quick analysis report"""
    print("\n" + "=" * 50)
    print("📊 QUICK ANALYSIS REPORT")
    print("=" * 50)
    
    # Repository overview
    repo_name = Path(results["repository"]).name
    print(f"\n📁 Repository: {repo_name}")
    print(f"🐍 Python files: {results['python_files']}")
    print(f"📏 Lines of code: {results['total_lines']:,}")
    
    # Quality indicators
    print(f"\n🎯 Quality Indicators:")
    for summary in results["analysis_summary"]:
        print(f"   {summary}")
    
    # Quick score calculation
    score = calculate_quick_score(results)
    grade = get_quick_grade(score)
    
    print(f"\n🏆 Quick Quality Score: {score}/100 ({grade})")
    
    # Recommendations
    print(f"\n💡 Quick Recommendations:")
    recommendations = get_quick_recommendations(results)
    for rec in recommendations:
        print(f"   • {rec}")
    
    # Next steps
    print(f"\n🚀 Next Steps:")
    print("   1. Fix any linting issues found")
    print("   2. Add the GitHub workflow to your repository")
    print("   3. Customize the configuration for your needs")
    print("   4. Set up comprehensive CI/CD analysis")
    
    print(f"\n📖 Full Setup Guide:")
    print("   See PYTHON_CODE_QUALITY_CICD.md for complete instructions")
    
    # Save results
    with open("quick-analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: quick-analysis.json")

def calculate_quick_score(results: Dict[str, Any]) -> int:
    """Calculate a quick quality score"""
    score = 0
    
    # File structure (25 points)
    if results["has_setup"]:
        score += 8
    if results["has_requirements"]:
        score += 8
    if results["has_readme"]:
        score += 9
    
    # Code quality (35 points)
    if results["python_files"] > 0:
        # Lint issues penalty
        lint_penalty = min(results["lint_issues"], 35)
        score += max(0, 35 - lint_penalty)
    
    # Testing (25 points)
    if results["test_files"] > 0:
        test_ratio = min(results["test_files"] / max(results["python_files"], 1), 1.0)
        score += int(test_ratio * 25)
    
    # Size bonus (15 points) - larger projects get some credit
    if results["total_lines"] > 100:
        score += 5
    if results["total_lines"] > 1000:
        score += 5
    if results["python_files"] > 5:
        score += 5
    
    return min(score, 100)

def get_quick_grade(score: int) -> str:
    """Convert score to letter grade"""
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 55:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"

def get_quick_recommendations(results: Dict[str, Any]) -> list:
    """Generate quick recommendations"""
    recommendations = []
    
    if not results["has_setup"]:
        recommendations.append("Add setup.py or pyproject.toml for package configuration")
    
    if not results["has_requirements"]:
        recommendations.append("Add requirements.txt or use Poetry for dependency management")
    
    if not results["has_readme"]:
        recommendations.append("Add a README.md file to document your project")
    
    if results["lint_issues"] > 10:
        recommendations.append(f"Fix {results['lint_issues']} linting issues (run 'ruff --fix .')")
    
    if results["test_files"] == 0:
        recommendations.append("Add unit tests to improve code reliability")
    
    if results["python_files"] > 0 and results["test_files"] / results["python_files"] < 0.3:
        recommendations.append("Increase test coverage (aim for 1 test file per 2-3 source files)")
    
    if not recommendations:
        recommendations.append("Good foundation! Consider adding type hints and documentation")
    
    return recommendations[:5]  # Limit to 5 recommendations

def should_exclude_file(file_path: Path) -> bool:
    """Check if file should be excluded"""
    exclude_patterns = [
        "__pycache__", ".git", ".venv", "venv", 
        ".env", ".pytest_cache", ".mypy_cache"
    ]
    
    path_str = str(file_path)
    return any(pattern in path_str for pattern in exclude_patterns)

def cleanup():
    """Cleanup temporary files"""
    # Clean up any temporary files created during analysis
    temp_files = ["quick-analysis.json"]
    for file in temp_files:
        if Path(file).exists():
            print(f"📁 Report saved: {file}")

if __name__ == "__main__":
    main()
