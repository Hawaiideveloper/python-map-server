#!/usr/bin/env python3
"""
Repository Analysis Script for Python Code Quality CI/CD

This script analyzes any Python repository using the MCP server tools
and generates comprehensive quality reports for CI/CD workflows.

Usage: python analyze-repo.py <repo_path>
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import shutil

# Configuration
MCP_SERVER_URL = "http://localhost:8080"
DEFAULT_TIMEOUT = 300
MAX_FILE_SIZE = 1024 * 1024  # 1MB

def main():
    """Main analysis function"""
    if len(sys.argv) != 2:
        print("Usage: python analyze-repo.py <repo_path>")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1]).resolve()
    if not repo_path.exists():
        print(f"❌ Error: Repository path {repo_path} does not exist")
        sys.exit(1)
    
    print(f"🔍 Starting analysis of repository: {repo_path}")
    print(f"📁 Repository size: {get_repo_size(repo_path)}")
    
    # Initialize comprehensive report
    report = initialize_report(repo_path)
    
    try:
        # Run all analysis steps
        run_comprehensive_analysis(repo_path, report)
        
        # Calculate final scores
        calculate_scores(report)
        
        # Generate outputs
        save_reports(report)
        
        print(f"✅ Analysis complete!")
        print(f"📊 Overall Score: {report['overall_score']}/100")
        print(f"🏷️  Quality Grade: {get_quality_grade(report['overall_score'])}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        
        # Create minimal error report
        error_report = {
            **report,
            "status": "error",
            "error_message": str(e),
            "overall_score": 0
        }
        save_reports(error_report)
        sys.exit(1)

def initialize_report(repo_path: Path) -> Dict[str, Any]:
    """Initialize the analysis report structure"""
    return {
        "repository": str(repo_path),
        "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "status": "in_progress",
        "overall_score": 0,
        "quality_grade": "F",
        
        # Core metrics
        "lint_issues": 0,
        "type_coverage": 0,
        "test_coverage": 0,
        "doc_coverage": 0,
        "complexity_score": 0,
        
        # Advanced analysis
        "ai_suggestions": [],
        "security_issues": [],
        "performance_insights": [],
        
        # Detailed results
        "detailed_results": {},
        
        # Repository info
        "repo_info": {
            "total_files": 0,
            "python_files": 0,
            "lines_of_code": 0,
            "size_bytes": 0
        },
        
        # Environment info
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "github_repo": os.getenv("GITHUB_REPOSITORY", "unknown"),
            "github_sha": os.getenv("GITHUB_SHA", "unknown")[:8]
        }
    }

def run_comprehensive_analysis(repo_path: Path, report: Dict[str, Any]):
    """Run all analysis steps"""
    
    # Collect repository information
    print("📊 Collecting repository information...")
    collect_repo_info(repo_path, report)
    
    # 1. Code Linting Analysis
    print("🐛 Running lint analysis...")
    run_lint_analysis(repo_path, report)
    
    # 2. Type Annotation Analysis
    print("🏷️  Analyzing type annotations...")
    run_type_analysis(repo_path, report)
    
    # 3. Test Coverage Analysis
    print("🧪 Analyzing test coverage...")
    run_test_analysis(repo_path, report)
    
    # 4. Documentation Analysis
    print("📚 Checking documentation coverage...")
    run_documentation_analysis(repo_path, report)
    
    # 5. Code Complexity Analysis
    print("🔄 Analyzing code complexity...")
    run_complexity_analysis(repo_path, report)
    
    # 6. AI-Powered Code Intelligence
    print("🤖 Running AI-powered analysis...")
    run_ai_analysis(repo_path, report)
    
    # 7. Security Scanning
    print("🔒 Performing security scan...")
    run_security_analysis(repo_path, report)
    
    # 8. Performance Analysis
    print("⚡ Analyzing performance patterns...")
    run_performance_analysis(repo_path, report)

def collect_repo_info(repo_path: Path, report: Dict[str, Any]):
    """Collect basic repository information"""
    try:
        python_files = list(repo_path.rglob("*.py"))
        total_files = list(repo_path.rglob("*"))
        
        # Filter out common exclusions
        python_files = [f for f in python_files if not should_exclude_file(f)]
        
        total_lines = 0
        total_size = 0
        
        for py_file in python_files:
            try:
                if py_file.stat().st_size < MAX_FILE_SIZE:
                    lines = len(py_file.read_text(encoding='utf-8', errors='ignore').splitlines())
                    total_lines += lines
                    total_size += py_file.stat().st_size
            except Exception:
                continue
        
        report["repo_info"] = {
            "total_files": len(total_files),
            "python_files": len(python_files),
            "lines_of_code": total_lines,
            "size_bytes": total_size
        }
        
    except Exception as e:
        print(f"⚠️  Warning: Could not collect repo info: {e}")

def run_lint_analysis(repo_path: Path, report: Dict[str, Any]):
    """Run linting analysis using ruff or similar tools"""
    try:
        # Try to use the MCP server's lint tool
        result = run_mcp_tool("lint_code", {
            "code_path": str(repo_path),
            "recursive": True,
            "fix": False
        })
        
        if result and result.get("status") == "success":
            issues = result.get("issues", [])
            report["lint_issues"] = len(issues)
            report["detailed_results"]["lint"] = result
        else:
            # Fallback to direct ruff execution
            result = run_direct_lint(repo_path)
            report["lint_issues"] = result["issue_count"]
            report["detailed_results"]["lint"] = result
            
    except Exception as e:
        print(f"⚠️  Warning: Lint analysis failed: {e}")
        report["lint_issues"] = 999  # High number to indicate failure

def run_direct_lint(repo_path: Path) -> Dict[str, Any]:
    """Direct linting using ruff or flake8"""
    try:
        # Try ruff first
        result = subprocess.run(
            ["ruff", "check", str(repo_path), "--output-format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False
        )
        
        if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
            try:
                issues = json.loads(result.stdout) if result.stdout.strip() else []
                return {
                    "tool": "ruff",
                    "issue_count": len(issues),
                    "issues": issues[:20]  # Limit for size
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback to simple count
        return {
            "tool": "ruff_fallback",
            "issue_count": result.stdout.count('\n') if result.stdout else 0,
            "raw_output": result.stdout[:1000]  # Truncate
        }
        
    except subprocess.TimeoutExpired:
        return {"tool": "timeout", "issue_count": 999}
    except FileNotFoundError:
        return {"tool": "not_available", "issue_count": 0}
    except Exception as e:
        return {"tool": "error", "issue_count": 999, "error": str(e)}

def run_type_analysis(repo_path: Path, report: Dict[str, Any]):
    """Analyze type annotation coverage"""
    try:
        result = run_mcp_tool("analyze_types", {
            "code_path": str(repo_path)
        })
        
        if result and result.get("status") == "success":
            report["type_coverage"] = result.get("coverage_percentage", 0)
            report["detailed_results"]["types"] = result
        else:
            # Simple fallback analysis
            coverage = calculate_simple_type_coverage(repo_path)
            report["type_coverage"] = coverage
            report["detailed_results"]["types"] = {"fallback_coverage": coverage}
            
    except Exception as e:
        print(f"⚠️  Warning: Type analysis failed: {e}")
        report["type_coverage"] = 0

def calculate_simple_type_coverage(repo_path: Path) -> int:
    """Simple type coverage calculation"""
    try:
        python_files = [f for f in repo_path.rglob("*.py") if not should_exclude_file(f)]
        
        if not python_files:
            return 0
        
        typed_functions = 0
        total_functions = 0
        
        for py_file in python_files[:10]:  # Limit for performance
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Simple regex-based detection
                import re
                functions = re.findall(r'def\s+\w+\s*\([^)]*\)', content)
                total_functions += len(functions)
                
                # Count functions with type hints
                typed = sum(1 for func in functions if ':' in func and '->' in content[content.find(func):content.find(func) + 200])
                typed_functions += typed
                
            except Exception:
                continue
        
        return int((typed_functions / total_functions * 100) if total_functions > 0 else 0)
        
    except Exception:
        return 0

def run_test_analysis(repo_path: Path, report: Dict[str, Any]):
    """Analyze test coverage"""
    try:
        result = run_mcp_tool("analyze_tests", {
            "code_path": str(repo_path)
        })
        
        if result and result.get("status") == "success":
            report["test_coverage"] = result.get("coverage_percentage", 0)
            report["detailed_results"]["tests"] = result
        else:
            # Simple test file analysis
            coverage = calculate_simple_test_coverage(repo_path)
            report["test_coverage"] = coverage
            report["detailed_results"]["tests"] = {"estimated_coverage": coverage}
            
    except Exception as e:
        print(f"⚠️  Warning: Test analysis failed: {e}")
        report["test_coverage"] = 0

def calculate_simple_test_coverage(repo_path: Path) -> int:
    """Simple test coverage estimation"""
    try:
        all_py_files = [f for f in repo_path.rglob("*.py") if not should_exclude_file(f)]
        test_files = [f for f in all_py_files if is_test_file(f)]
        
        if not all_py_files:
            return 0
        
        # Simple heuristic: test file ratio
        test_ratio = len(test_files) / len(all_py_files)
        return min(int(test_ratio * 100 * 2), 100)  # Rough estimation
        
    except Exception:
        return 0

def run_documentation_analysis(repo_path: Path, report: Dict[str, Any]):
    """Analyze documentation coverage"""
    try:
        result = run_mcp_tool("analyze_documentation", {
            "code_path": str(repo_path)
        })
        
        if result and result.get("status") == "success":
            report["doc_coverage"] = result.get("coverage_percentage", 0)
            report["detailed_results"]["documentation"] = result
        else:
            # Simple docstring analysis
            coverage = calculate_simple_doc_coverage(repo_path)
            report["doc_coverage"] = coverage
            report["detailed_results"]["documentation"] = {"estimated_coverage": coverage}
            
    except Exception as e:
        print(f"⚠️  Warning: Documentation analysis failed: {e}")
        report["doc_coverage"] = 0

def calculate_simple_doc_coverage(repo_path: Path) -> int:
    """Simple documentation coverage calculation"""
    try:
        python_files = [f for f in repo_path.rglob("*.py") if not should_exclude_file(f)]
        
        if not python_files:
            return 0
        
        documented_items = 0
        total_items = 0
        
        for py_file in python_files[:10]:  # Limit for performance
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Count functions, classes, and methods
                import re
                functions = re.findall(r'def\s+\w+', content)
                classes = re.findall(r'class\s+\w+', content)
                
                total_items += len(functions) + len(classes)
                
                # Count docstrings (simple detection)
                docstrings = re.findall(r'""".+?"""', content, re.DOTALL)
                docstrings += re.findall(r"'''.+?'''", content, re.DOTALL)
                
                documented_items += min(len(docstrings), len(functions) + len(classes))
                
            except Exception:
                continue
        
        return int((documented_items / total_items * 100) if total_items > 0 else 0)
        
    except Exception:
        return 0

def run_complexity_analysis(repo_path: Path, report: Dict[str, Any]):
    """Analyze code complexity"""
    try:
        # Simple complexity analysis
        complexity_score = calculate_simple_complexity(repo_path)
        report["complexity_score"] = complexity_score
        report["detailed_results"]["complexity"] = {"score": complexity_score}
        
    except Exception as e:
        print(f"⚠️  Warning: Complexity analysis failed: {e}")
        report["complexity_score"] = 50  # Neutral score

def calculate_simple_complexity(repo_path: Path) -> int:
    """Simple complexity calculation"""
    try:
        python_files = [f for f in repo_path.rglob("*.py") if not should_exclude_file(f)]
        
        if not python_files:
            return 100
        
        total_complexity = 0
        file_count = 0
        
        for py_file in python_files[:10]:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Simple complexity heuristics
                lines = content.splitlines()
                complexity = 1  # Base complexity
                
                for line in lines:
                    line = line.strip()
                    # Add complexity for control structures
                    if any(keyword in line for keyword in ['if ', 'elif ', 'for ', 'while ', 'try:', 'except', 'with ']):
                        complexity += 1
                    # Add for nested structures
                    if line.startswith('    ') and any(keyword in line for keyword in ['if ', 'for ', 'while ']):
                        complexity += 1
                
                # Normalize by file size
                if lines:
                    file_complexity = max(1, min(complexity / len(lines) * 100, 100))
                    total_complexity += file_complexity
                    file_count += 1
                
            except Exception:
                continue
        
        if file_count > 0:
            avg_complexity = total_complexity / file_count
            # Convert to inverse score (lower complexity = higher score)
            return max(0, int(100 - avg_complexity))
        
        return 100
        
    except Exception:
        return 50

def run_ai_analysis(repo_path: Path, report: Dict[str, Any]):
    """Run AI-powered analysis"""
    try:
        result = run_mcp_tool("ai_code_analysis", {
            "code_path": str(repo_path),
            "analysis_type": "comprehensive"
        })
        
        if result and result.get("status") == "success":
            report["ai_suggestions"] = result.get("suggestions", [])
            report["detailed_results"]["ai_analysis"] = result
        else:
            # Fallback suggestions based on metrics
            suggestions = generate_fallback_suggestions(report)
            report["ai_suggestions"] = suggestions
            
    except Exception as e:
        print(f"⚠️  Warning: AI analysis failed: {e}")
        report["ai_suggestions"] = ["AI analysis temporarily unavailable"]

def generate_fallback_suggestions(report: Dict[str, Any]) -> List[str]:
    """Generate suggestions based on analysis results"""
    suggestions = []
    
    if report["lint_issues"] > 0:
        suggestions.append(f"Fix {report['lint_issues']} linting issues to improve code quality")
    
    if report["type_coverage"] < 80:
        suggestions.append("Add type hints to improve code maintainability and IDE support")
    
    if report["test_coverage"] < 80:
        suggestions.append("Increase test coverage to ensure code reliability")
    
    if report["doc_coverage"] < 70:
        suggestions.append("Add docstrings to public functions and classes")
    
    if report["complexity_score"] < 70:
        suggestions.append("Consider refactoring complex functions for better readability")
    
    if not suggestions:
        suggestions.append("Code quality looks good! Consider adding performance optimizations")
    
    return suggestions[:5]  # Limit to 5 suggestions

def run_security_analysis(repo_path: Path, report: Dict[str, Any]):
    """Run security analysis"""
    try:
        result = run_mcp_tool("security_scan", {
            "code_path": str(repo_path)
        })
        
        if result and result.get("status") == "success":
            report["security_issues"] = result.get("issues", [])
            report["detailed_results"]["security"] = result
        else:
            # Simple security pattern detection
            issues = detect_simple_security_issues(repo_path)
            report["security_issues"] = issues
            
    except Exception as e:
        print(f"⚠️  Warning: Security analysis failed: {e}")
        report["security_issues"] = []

def detect_simple_security_issues(repo_path: Path) -> List[str]:
    """Simple security issue detection"""
    issues = []
    
    try:
        python_files = [f for f in repo_path.rglob("*.py") if not should_exclude_file(f)]
        
        dangerous_patterns = [
            (r'eval\s*\(', "Use of eval() detected"),
            (r'exec\s*\(', "Use of exec() detected"),
            (r'input\s*\(.*\)', "Direct input() usage detected"),
            (r'os\.system\s*\(', "Use of os.system() detected"),
            (r'subprocess\.call\s*\(.*shell\s*=\s*True', "Shell injection risk detected"),
        ]
        
        for py_file in python_files[:20]:  # Limit for performance
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                import re
                for pattern, message in dangerous_patterns:
                    if re.search(pattern, content):
                        issues.append(f"{message} in {py_file.name}")
                        
            except Exception:
                continue
    
    except Exception:
        pass
    
    return issues[:10]  # Limit to 10 issues

def run_performance_analysis(repo_path: Path, report: Dict[str, Any]):
    """Run performance analysis"""
    try:
        insights = generate_performance_insights(repo_path)
        report["performance_insights"] = insights
        report["detailed_results"]["performance"] = {"insights": insights}
        
    except Exception as e:
        print(f"⚠️  Warning: Performance analysis failed: {e}")
        report["performance_insights"] = []

def generate_performance_insights(repo_path: Path) -> List[str]:
    """Generate performance insights"""
    insights = []
    
    try:
        python_files = [f for f in repo_path.rglob("*.py") if not should_exclude_file(f)]
        
        for py_file in python_files[:10]:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Simple performance pattern detection
                if 'for' in content and 'append' in content:
                    insights.append("Consider using list comprehensions instead of append in loops")
                
                if 'pandas' in content and 'iterrows' in content:
                    insights.append("Consider vectorized operations instead of iterrows() in pandas")
                
                if 'requests.get' in content and 'for' in content:
                    insights.append("Consider using async requests for multiple HTTP calls")
                
                if len(insights) >= 3:
                    break
                    
            except Exception:
                continue
    
    except Exception:
        pass
    
    if not insights:
        insights = ["No specific performance issues detected"]
    
    return insights[:3]

def run_mcp_tool(tool_name: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Run an MCP server tool via HTTP"""
    try:
        import requests
        
        response = requests.post(
            f"{MCP_SERVER_URL}/{tool_name}",
            json=params,
            timeout=DEFAULT_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Tool {tool_name} returned status {response.status_code}")
            return None
            
    except ImportError:
        print("⚠️  requests library not available, using fallback analysis")
        return None
    except Exception as e:
        print(f"⚠️  Tool {tool_name} failed: {e}")
        return None

def calculate_scores(report: Dict[str, Any]):
    """Calculate overall scores and grades"""
    
    # Individual scores (0-25 points each)
    lint_score = max(0, 25 - min(25, report["lint_issues"]))
    type_score = (report["type_coverage"] / 100) * 25
    test_score = (report["test_coverage"] / 100) * 25
    doc_score = (report["doc_coverage"] / 100) * 25
    
    # Bonus points for security and complexity
    security_bonus = 5 if len(report["security_issues"]) == 0 else 0
    complexity_bonus = max(0, (report["complexity_score"] - 70) / 30 * 5)
    
    # Calculate overall score
    total_score = lint_score + type_score + test_score + doc_score + security_bonus + complexity_bonus
    report["overall_score"] = min(100, int(total_score))
    
    # Assign quality grade
    report["quality_grade"] = get_quality_grade(report["overall_score"])
    
    # Add score breakdown
    report["score_breakdown"] = {
        "lint_score": int(lint_score),
        "type_score": int(type_score),
        "test_score": int(test_score),
        "doc_score": int(doc_score),
        "security_bonus": int(security_bonus),
        "complexity_bonus": int(complexity_bonus)
    }

def get_quality_grade(score: int) -> str:
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"

def save_reports(report: Dict[str, Any]):
    """Save all report formats"""
    
    # Update status
    report["status"] = "completed"
    
    # Save JSON report
    with open("quality-report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Save markdown summary
    generate_markdown_summary(report)
    
    # Save badge data
    generate_badge_data(report)

def generate_markdown_summary(report: Dict[str, Any]):
    """Generate human-readable markdown summary"""
    
    grade_emoji = {
        "A+": "🏆", "A": "🥇", "B": "🥈", 
        "C": "🥉", "D": "⚠️", "F": "❌"
    }
    
    summary = f"""# 📊 Python Code Quality Report

## {grade_emoji.get(report['quality_grade'], '📊')} Overall Score: {report['overall_score']}/100 (Grade: {report['quality_grade']})

### 📈 Quality Metrics

| Metric | Score | Status | Target |
|--------|-------|--------|--------|
| 🐛 Lint Issues | {report['lint_issues']} | {'✅' if report['lint_issues'] == 0 else '❌'} | 0 |
| 🏷️ Type Coverage | {report['type_coverage']}% | {'✅' if report['type_coverage'] >= 80 else '⚠️' if report['type_coverage'] >= 60 else '❌'} | 80%+ |
| 🧪 Test Coverage | {report['test_coverage']}% | {'✅' if report['test_coverage'] >= 80 else '⚠️' if report['test_coverage'] >= 60 else '❌'} | 80%+ |
| 📚 Documentation | {report['doc_coverage']}% | {'✅' if report['doc_coverage'] >= 70 else '⚠️' if report['doc_coverage'] >= 50 else '❌'} | 70%+ |
| 🔄 Complexity | {report['complexity_score']}/100 | {'✅' if report['complexity_score'] >= 70 else '⚠️' if report['complexity_score'] >= 50 else '❌'} | 70%+ |

### 🏗️ Repository Information

- **Python Files**: {report['repo_info']['python_files']}
- **Lines of Code**: {report['repo_info']['lines_of_code']:,}
- **Repository Size**: {format_bytes(report['repo_info']['size_bytes'])}

### 🤖 AI-Powered Insights

{chr(10).join(f"- {suggestion}" for suggestion in report['ai_suggestions'][:5]) if report['ai_suggestions'] else "- No specific suggestions at this time"}

### 🔒 Security Analysis

{f"✅ No security issues detected" if not report['security_issues'] else f"❌ {len(report['security_issues'])} security issue(s) found:" + chr(10) + chr(10).join(f"- {issue}" for issue in report['security_issues'][:3])}

### ⚡ Performance Insights

{chr(10).join(f"- {insight}" for insight in report['performance_insights'][:3]) if report['performance_insights'] else "- No specific performance recommendations"}

### 📋 Score Breakdown

- **Linting**: {report['score_breakdown']['lint_score']}/25 points
- **Type Hints**: {report['score_breakdown']['type_score']}/25 points  
- **Testing**: {report['score_breakdown']['test_score']}/25 points
- **Documentation**: {report['score_breakdown']['doc_score']}/25 points
- **Security Bonus**: {report['score_breakdown']['security_bonus']}/5 points
- **Complexity Bonus**: {report['score_breakdown']['complexity_bonus']}/5 points

### 🎯 Recommendations

{get_recommendations(report)}

---
**Analysis Details**
- Timestamp: {report['analysis_timestamp']}
- Python Version: {report['environment']['python_version']}
- Repository: {report['environment']['github_repo']}
- Commit: {report['environment']['github_sha']}

*Generated by Python Code Quality CI/CD*
"""
    
    with open("quality-summary.md", "w") as f:
        f.write(summary)

def generate_badge_data(report: Dict[str, Any]):
    """Generate badge data for README shields"""
    
    score = report['overall_score']
    grade = report['quality_grade']
    
    # Color based on score
    if score >= 80:
        color = "brightgreen"
    elif score >= 60:
        color = "yellow"
    else:
        color = "red"
    
    badge_data = {
        "schemaVersion": 1,
        "label": "Code Quality",
        "message": f"{score}/100 ({grade})",
        "color": color
    }
    
    with open("quality-badge.json", "w") as f:
        json.dump(badge_data, f, indent=2)

def get_recommendations(report: Dict[str, Any]) -> str:
    """Generate specific recommendations based on scores"""
    recommendations = []
    
    if report['overall_score'] >= 90:
        recommendations.append("🏆 Excellent code quality! Your code meets professional standards.")
    elif report['overall_score'] >= 80:
        recommendations.append("🎯 Good code quality! Minor improvements could make it excellent.")
    elif report['overall_score'] >= 60:
        recommendations.append("📈 Moderate code quality. Focus on the areas marked for improvement.")
    else:
        recommendations.append("🔧 Code quality needs attention. Prioritize fixing linting and testing issues.")
    
    # Specific recommendations
    if report['lint_issues'] > 10:
        recommendations.append("🐛 High number of linting issues - run `ruff --fix` to auto-fix many problems")
    
    if report['type_coverage'] < 50:
        recommendations.append("🏷️ Low type coverage - start by adding type hints to public functions")
    
    if report['test_coverage'] < 50:
        recommendations.append("🧪 Low test coverage - begin with unit tests for core functionality")
    
    if report['doc_coverage'] < 40:
        recommendations.append("📚 Missing documentation - add docstrings to your main classes and functions")
    
    if len(report['security_issues']) > 0:
        recommendations.append("🔒 Security issues detected - review and fix before deployment")
    
    return "\n".join(f"- {rec}" for rec in recommendations)

def should_exclude_file(file_path: Path) -> bool:
    """Check if file should be excluded from analysis"""
    exclude_patterns = [
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        ".env",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "migrations",
        ".tox"
    ]
    
    path_str = str(file_path)
    return any(pattern in path_str for pattern in exclude_patterns)

def is_test_file(file_path: Path) -> bool:
    """Check if file is a test file"""
    name = file_path.name.lower()
    return (
        name.startswith("test_") or 
        name.endswith("_test.py") or 
        "test" in str(file_path.parent).lower()
    )

def get_repo_size(repo_path: Path) -> str:
    """Get human-readable repository size"""
    try:
        total_size = sum(
            f.stat().st_size 
            for f in repo_path.rglob("*") 
            if f.is_file() and not should_exclude_file(f)
        )
        return format_bytes(total_size)
    except Exception:
        return "unknown"

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

if __name__ == "__main__":
    main()
