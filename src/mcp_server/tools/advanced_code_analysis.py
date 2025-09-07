"""
Advanced code analysis tools for modern Python development.

This module provides comprehensive code analysis including type checking,
security scanning, performance analysis, and modern Python feature detection.
"""

import ast
import json
import os
import subprocess
import tempfile
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..utils.logging import log_tool_execution
from ..utils.security import validate_code_safety


@log_tool_execution("type_check_mypy")
def type_check_code(code: str, python_version: str = "3.12") -> Dict[str, Any]:
    """
    Perform type checking using mypy with modern Python features.
    
    Args:
        code: Python code to type check
        python_version: Target Python version (3.8, 3.9, 3.10, 3.11, 3.12)
        
    Returns:
        Dict with type checking results and suggestions
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        # Create temporary file for mypy analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
            
        try:
            # Run mypy with modern Python features
            result = subprocess.run([
                "mypy", 
                "--python-version", python_version,
                "--strict",
                "--show-error-codes",
                "--show-column-numbers", 
                "--show-error-context",
                "--pretty",
                tmp_path
            ], capture_output=True, text=True, timeout=30)
            
            # Parse mypy output
            issues = []
            suggestions = []
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ':' in line and ('error:' in line or 'warning:' in line):
                        parts = line.split(':', 4)
                        if len(parts) >= 4:
                            issue = {
                                "line": int(parts[1]) if parts[1].isdigit() else 0,
                                "column": int(parts[2]) if parts[2].isdigit() else 0,
                                "severity": "error" if "error:" in line else "warning",
                                "message": parts[-1].strip(),
                                "code": extract_error_code(line)
                            }
                            issues.append(issue)
                            
                            # Generate type hints suggestions
                            if "implicit Any" in line or "untyped" in line:
                                suggestions.append({
                                    "type": "add_type_hints",
                                    "line": issue["line"],
                                    "message": "Consider adding explicit type annotations",
                                    "severity": "medium"
                                })
                                
            return {
                "status": "success",
                "result": {
                    "issues": issues,
                    "suggestions": suggestions,
                    "python_version": python_version,
                    "total_issues": len(issues),
                    "type_coverage": calculate_type_coverage(code),
                    "modern_features": detect_modern_python_features(code)
                }
            }
            
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "type_check_mypy"
        }


@log_tool_execution("security_scan_bandit")
def security_scan(code: str, confidence_level: str = "medium") -> Dict[str, Any]:
    """
    Perform security analysis using bandit.
    
    Args:
        code: Python code to scan
        confidence_level: Confidence level (low, medium, high)
        
    Returns:
        Dict with security issues and recommendations
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        # Validate code safety first
        safety_check = validate_code_safety(code)
        if not safety_check["is_safe"]:
            return {
                "status": "error",
                "error": f"Code safety violation: {safety_check['reason']}",
                "tool": "security_scan_bandit"
            }
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
            
        try:
            # Run bandit security scanner
            result = subprocess.run([
                "bandit", 
                "-f", "json",
                "-c", confidence_level,
                tmp_path
            ], capture_output=True, text=True, timeout=30)
            
            # Parse bandit JSON output
            security_issues = []
            if result.stdout:
                try:
                    bandit_data = json.loads(result.stdout)
                    for issue in bandit_data.get("results", []):
                        security_issues.append({
                            "test_id": issue.get("test_id"),
                            "test_name": issue.get("test_name"),
                            "severity": issue.get("issue_severity", "UNKNOWN").lower(),
                            "confidence": issue.get("issue_confidence", "UNKNOWN").lower(),
                            "line": issue.get("line_number", 0),
                            "code": issue.get("code", ""),
                            "message": issue.get("issue_text", ""),
                            "more_info": issue.get("more_info", "")
                        })
                except json.JSONDecodeError:
                    pass
                    
            # Generate security recommendations
            recommendations = generate_security_recommendations(security_issues)
            
            return {
                "status": "success",
                "result": {
                    "security_issues": security_issues,
                    "recommendations": recommendations,
                    "risk_score": calculate_risk_score(security_issues),
                    "confidence_level": confidence_level,
                    "total_issues": len(security_issues)
                }
            }
            
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "security_scan_bandit"
        }


@log_tool_execution("dependency_audit")
def audit_dependencies(requirements_content: str = "") -> Dict[str, Any]:
    """
    Audit dependencies for security vulnerabilities using safety.
    
    Args:
        requirements_content: Content of requirements.txt or pyproject.toml
        
    Returns:
        Dict with vulnerability scan results
    """
    try:
        if not requirements_content:
            # Try to read from current project
            possible_files = ["requirements.txt", "pyproject.toml", "Pipfile"]
            for filename in possible_files:
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        requirements_content = f.read()
                    break
                    
        if not requirements_content:
            return {
                "status": "warning",
                "message": "No dependency file provided or found",
                "tool": "dependency_audit"
            }
            
        # Create temporary requirements file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            # Convert pyproject.toml to requirements.txt format if needed
            if requirements_content.strip().startswith('['):
                requirements_content = extract_requirements_from_pyproject(requirements_content)
            tmp.write(requirements_content)
            tmp_path = tmp.name
            
        try:
            # Run safety check
            result = subprocess.run([
                "safety", "check", 
                "--json",
                "-r", tmp_path
            ], capture_output=True, text=True, timeout=60)
            
            vulnerabilities = []
            if result.stdout:
                try:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        vulnerabilities.append({
                            "package": vuln.get("package_name"),
                            "installed_version": vuln.get("installed_version"),
                            "vulnerability_id": vuln.get("vulnerability_id"),
                            "advisory": vuln.get("advisory"),
                            "fixed_versions": vuln.get("fixed_versions", []),
                            "severity": determine_severity(vuln.get("advisory", ""))
                        })
                except json.JSONDecodeError:
                    pass
                    
            return {
                "status": "success",
                "result": {
                    "vulnerabilities": vulnerabilities,
                    "total_vulnerabilities": len(vulnerabilities),
                    "recommendations": generate_dependency_recommendations(vulnerabilities),
                    "security_score": calculate_security_score(vulnerabilities)
                }
            }
            
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "dependency_audit"
        }


@log_tool_execution("code_completion")
def intelligent_code_completion(code: str, cursor_position: int = -1) -> Dict[str, Any]:
    """
    Provide intelligent code completion using Jedi.
    
    Args:
        code: Python code for completion
        cursor_position: Cursor position in code (-1 for end)
        
    Returns:
        Dict with completion suggestions
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        try:
            import jedi
        except ImportError:
            return {
                "status": "error",
                "error": "jedi not installed. Install with: pip install jedi",
                "tool": "code_completion"
            }
            
        if cursor_position == -1:
            cursor_position = len(code)
            
        # Calculate line and column from position
        lines = code[:cursor_position].split('\n')
        line_num = len(lines)
        col_num = len(lines[-1])
        
        # Get completions from Jedi
        script = jedi.Script(code=code, line=line_num, column=col_num)
        completions = script.completions()
        
        suggestions = []
        for completion in completions[:50]:  # Limit to 50 suggestions
            suggestions.append({
                "name": completion.name,
                "complete": completion.complete,
                "type": completion.type,
                "description": completion.description,
                "docstring": completion.docstring(),
                "module_name": completion.module_name
            })
            
        # Also get definitions and references
        definitions = []
        try:
            defs = script.goto_definitions()
            for definition in defs:
                definitions.append({
                    "name": definition.name,
                    "type": definition.type,
                    "module_name": definition.module_name,
                    "line": definition.line,
                    "column": definition.column,
                    "description": definition.description
                })
        except Exception:
            pass
            
        return {
            "status": "success",
            "result": {
                "completions": suggestions,
                "definitions": definitions,
                "cursor_position": cursor_position,
                "line": line_num,
                "column": col_num,
                "context": get_completion_context(code, cursor_position)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "code_completion"
        }


@log_tool_execution("modern_python_analysis")
def analyze_modern_python_features(code: str) -> Dict[str, Any]:
    """
    Analyze code for modern Python features and suggest improvements.
    
    Args:
        code: Python code to analyze
        
    Returns:
        Dict with modern feature analysis and suggestions
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        tree = ast.parse(code)
        
        # Detect current Python features
        current_features = detect_modern_python_features(code)
        
        # Suggest modern replacements
        suggestions = []
        
        # Check for old-style string formatting
        if "%" in code and "%" not in [node for node in ast.walk(tree) if isinstance(node, ast.Mod)]:
            suggestions.append({
                "type": "string_formatting",
                "message": "Consider using f-strings for better performance and readability",
                "severity": "medium",
                "example": "f'{variable}' instead of '%s' % variable"
            })
            
        # Check for missing type hints
        functions_without_hints = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.returns and not any(arg.annotation for arg in node.args.args):
                    functions_without_hints.append(node.name)
                    
        if functions_without_hints:
            suggestions.append({
                "type": "type_hints",
                "message": f"Add type hints to functions: {', '.join(functions_without_hints[:5])}",
                "severity": "medium",
                "python_version": "3.5+"
            })
            
        # Check for dataclass opportunities
        classes_for_dataclass = detect_dataclass_opportunities(tree)
        if classes_for_dataclass:
            suggestions.append({
                "type": "dataclass",
                "message": f"Consider using @dataclass for: {', '.join(classes_for_dataclass)}",
                "severity": "low",
                "python_version": "3.7+"
            })
            
        # Check for walrus operator opportunities
        walrus_opportunities = detect_walrus_opportunities(code)
        if walrus_opportunities:
            suggestions.append({
                "type": "walrus_operator",
                "message": "Consider using walrus operator (:=) for assignment expressions",
                "severity": "low",
                "python_version": "3.8+",
                "count": len(walrus_opportunities)
            })
            
        # Detect match statement opportunities (Python 3.10+)
        match_opportunities = detect_match_opportunities(tree)
        if match_opportunities:
            suggestions.append({
                "type": "match_statement",
                "message": "Consider using match statements instead of if/elif chains",
                "severity": "low", 
                "python_version": "3.10+",
                "count": len(match_opportunities)
            })
            
        return {
            "status": "success",
            "result": {
                "current_features": current_features,
                "suggestions": suggestions,
                "modernization_score": calculate_modernization_score(current_features, suggestions),
                "target_python_version": "3.12",
                "compatibility": check_version_compatibility(tree)
            }
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "modern_python_analysis"
        }


# Helper functions
def extract_error_code(line: str) -> Optional[str]:
    """Extract error code from mypy output."""
    import re
    match = re.search(r'\[([a-z-]+)\]', line)
    return match.group(1) if match else None


def calculate_type_coverage(code: str) -> float:
    """Calculate percentage of functions with type hints."""
    try:
        tree = ast.parse(code)
        total_functions = 0
        typed_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if node.returns or any(arg.annotation for arg in node.args.args):
                    typed_functions += 1
                    
        return (typed_functions / total_functions * 100) if total_functions > 0 else 100
    except:
        return 0


def detect_modern_python_features(code: str) -> Dict[str, bool]:
    """Detect modern Python features in code."""
    features = {
        "f_strings": "f'" in code or 'f"' in code,
        "type_hints": "->" in code or ": " in code,
        "dataclasses": "@dataclass" in code,
        "async_await": "async " in code and "await " in code,
        "context_managers": "with " in code,
        "comprehensions": "[" in code and "for " in code,
        "walrus_operator": ":=" in code,
        "match_statements": "match " in code and "case " in code,
        "union_types": " | " in code,  # Python 3.10+ union syntax
        "generic_types": "Generic[" in code or "TypeVar" in code
    }
    
    try:
        tree = ast.parse(code)
        # Check for more complex features in AST
        for node in ast.walk(tree):
            if isinstance(node, ast.NamedExpr):  # Walrus operator
                features["walrus_operator"] = True
            elif isinstance(node, ast.Match):  # Match statements
                features["match_statements"] = True
                
    except:
        pass
        
    return features


def generate_security_recommendations(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate security recommendations based on issues."""
    recommendations = []
    
    for issue in issues:
        test_id = issue.get("test_id", "")
        
        if "hardcoded_password" in test_id:
            recommendations.append({
                "type": "hardcoded_secrets",
                "message": "Use environment variables or secure vaults for secrets",
                "priority": "high"
            })
        elif "sql_injection" in test_id:
            recommendations.append({
                "type": "sql_injection",
                "message": "Use parameterized queries or ORM to prevent SQL injection",
                "priority": "critical"
            })
        elif "shell_injection" in test_id:
            recommendations.append({
                "type": "shell_injection", 
                "message": "Avoid shell=True in subprocess calls, validate inputs",
                "priority": "high"
            })
            
    return recommendations


def calculate_risk_score(issues: List[Dict[str, Any]]) -> int:
    """Calculate overall risk score based on security issues."""
    score = 0
    severity_weights = {"low": 1, "medium": 3, "high": 5}
    
    for issue in issues:
        severity = issue.get("severity", "low")
        score += severity_weights.get(severity, 1)
        
    return min(score, 100)


def extract_requirements_from_pyproject(content: str) -> str:
    """Extract requirements from pyproject.toml content."""
    # Simplified extraction - in practice, use tomli/tomllib
    lines = []
    in_dependencies = False
    
    for line in content.split('\n'):
        if '[tool.poetry.dependencies]' in line:
            in_dependencies = True
            continue
        elif line.startswith('[') and in_dependencies:
            break
        elif in_dependencies and '=' in line:
            package = line.split('=')[0].strip().strip('"')
            if package and package != "python":
                lines.append(package)
                
    return '\n'.join(lines)


def determine_severity(advisory: str) -> str:
    """Determine severity from advisory text."""
    advisory_lower = advisory.lower()
    if any(word in advisory_lower for word in ["critical", "remote code execution", "rce"]):
        return "critical"
    elif any(word in advisory_lower for word in ["high", "privilege escalation", "sql injection"]):
        return "high"
    elif any(word in advisory_lower for word in ["medium", "denial of service", "dos"]):
        return "medium"
    else:
        return "low"


def generate_dependency_recommendations(vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate recommendations for dependency vulnerabilities."""
    recommendations = []
    
    for vuln in vulnerabilities:
        package = vuln.get("package", "")
        fixed_versions = vuln.get("fixed_versions", [])
        
        if fixed_versions:
            recommendations.append({
                "type": "update_package",
                "package": package,
                "message": f"Update {package} to version {fixed_versions[0]} or later",
                "priority": vuln.get("severity", "medium")
            })
        else:
            recommendations.append({
                "type": "replace_package",
                "package": package,
                "message": f"Consider replacing {package} with a secure alternative",
                "priority": "high"
            })
            
    return recommendations


def calculate_security_score(vulnerabilities: List[Dict[str, Any]]) -> int:
    """Calculate security score based on vulnerabilities."""
    if not vulnerabilities:
        return 100
        
    severity_weights = {"low": 5, "medium": 15, "high": 30, "critical": 50}
    penalty = sum(severity_weights.get(v.get("severity", "low"), 5) for v in vulnerabilities)
    
    return max(0, 100 - penalty)


def get_completion_context(code: str, position: int) -> Dict[str, Any]:
    """Get context around completion position."""
    lines = code[:position].split('\n')
    current_line = lines[-1] if lines else ""
    
    return {
        "current_line": current_line,
        "line_number": len(lines),
        "in_function": "def " in '\n'.join(lines[-10:]),
        "in_class": "class " in '\n'.join(lines[-20:]),
        "indent_level": len(current_line) - len(current_line.lstrip())
    }


def detect_dataclass_opportunities(tree: ast.AST) -> List[str]:
    """Detect classes that could benefit from @dataclass."""
    candidates = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Look for classes with simple __init__ methods
            has_simple_init = False
            for item in node.body:
                if (isinstance(item, ast.FunctionDef) and 
                    item.name == "__init__" and
                    len(item.body) < 10):  # Simple heuristic
                    has_simple_init = True
                    break
                    
            if has_simple_init and "@dataclass" not in ast.get_source_segment("", node):
                candidates.append(node.name)
                
    return candidates


def detect_walrus_opportunities(code: str) -> List[str]:
    """Detect opportunities for walrus operator usage."""
    opportunities = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines):
        # Simple pattern: if var = func() followed by if var:
        if (i < len(lines) - 1 and
            "=" in line and "if " not in line and
            "if " + line.split("=")[0].strip() in lines[i + 1]):
            opportunities.append(f"Line {i + 1}")
            
    return opportunities


def detect_match_opportunities(tree: ast.AST) -> List[str]:
    """Detect long if/elif chains that could use match statements."""
    opportunities = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            elif_count = 0
            current = node
            
            while hasattr(current, 'orelse') and current.orelse:
                if (len(current.orelse) == 1 and 
                    isinstance(current.orelse[0], ast.If)):
                    elif_count += 1
                    current = current.orelse[0]
                else:
                    break
                    
            if elif_count >= 3:  # 3+ elif statements
                opportunities.append(f"Line {node.lineno}")
                
    return opportunities


def calculate_modernization_score(features: Dict[str, bool], suggestions: List[Dict[str, Any]]) -> int:
    """Calculate modernization score."""
    modern_features = sum(1 for used in features.values() if used)
    total_features = len(features)
    
    base_score = (modern_features / total_features * 100) if total_features > 0 else 0
    
    # Deduct points for suggestions
    penalty = len(suggestions) * 5
    
    return max(0, int(base_score - penalty))


def check_version_compatibility(tree: ast.AST) -> Dict[str, str]:
    """Check Python version compatibility."""
    min_version = "3.8"
    
    for node in ast.walk(tree):
        if isinstance(node, ast.NamedExpr):  # Walrus operator
            min_version = max(min_version, "3.8")
        elif isinstance(node, ast.Match):  # Match statements
            min_version = max(min_version, "3.10")
            
    return {
        "minimum_version": min_version,
        "recommended_version": "3.12",
        "compatibility_level": "high" if min_version <= "3.9" else "medium"
    }

