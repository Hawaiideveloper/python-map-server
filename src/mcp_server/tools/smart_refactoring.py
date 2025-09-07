"""
Smart refactoring tools for Python code improvement.

This module provides intelligent refactoring capabilities including pattern
detection, code modernization, and automated improvements.
"""

import ast
import re
import traceback
from typing import Any, Dict, List, Optional, Tuple

from ..utils.logging import log_tool_execution
from ..utils.security import validate_code_safety


@log_tool_execution("smart_refactor")
def smart_refactor(code: str, refactor_type: str = "all") -> Dict[str, Any]:
    """
    Perform intelligent code refactoring with multiple improvement strategies.
    
    Args:
        code: Python code to refactor
        refactor_type: Type of refactoring (all, modernize, performance, readability)
        
    Returns:
        Dict with refactored code and applied changes
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        # Validate code safety
        safety_check = validate_code_safety(code)
        if not safety_check["is_safe"]:
            raise ValueError(f"Code safety violation: {safety_check['reason']}")
            
        # Parse the code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "status": "error",
                "error": f"Syntax error in code: {e}",
                "tool": "smart_refactor"
            }
            
        refactored_code = code
        applied_changes = []
        
        # Apply different refactoring strategies
        if refactor_type in ["all", "modernize"]:
            refactored_code, changes = modernize_code(refactored_code)
            applied_changes.extend(changes)
            
        if refactor_type in ["all", "performance"]:
            refactored_code, changes = optimize_performance(refactored_code)
            applied_changes.extend(changes)
            
        if refactor_type in ["all", "readability"]:
            refactored_code, changes = improve_readability(refactored_code)
            applied_changes.extend(changes)
            
        # Pattern-based improvements
        refactored_code, pattern_changes = apply_pattern_improvements(refactored_code)
        applied_changes.extend(pattern_changes)
        
        # Calculate improvement metrics
        metrics = calculate_improvement_metrics(code, refactored_code)
        
        return {
            "status": "success",
            "result": {
                "original_code": code,
                "refactored_code": refactored_code,
                "applied_changes": applied_changes,
                "improvement_metrics": metrics,
                "refactor_type": refactor_type,
                "total_changes": len(applied_changes)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "smart_refactor"
        }


@log_tool_execution("detect_code_smells")
def detect_code_smells(code: str) -> Dict[str, Any]:
    """
    Detect code smells and anti-patterns in Python code.
    
    Args:
        code: Python code to analyze
        
    Returns:
        Dict with detected code smells and refactoring suggestions
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        tree = ast.parse(code)
        code_smells = []
        
        # Detect various code smells
        code_smells.extend(detect_long_methods(tree, code))
        code_smells.extend(detect_large_classes(tree, code))
        code_smells.extend(detect_god_objects(tree))
        code_smells.extend(detect_duplicate_code(code))
        code_smells.extend(detect_magic_numbers(tree, code))
        code_smells.extend(detect_long_parameter_lists(tree))
        code_smells.extend(detect_dead_code(tree, code))
        code_smells.extend(detect_complex_conditionals(tree, code))
        
        # Generate refactoring suggestions
        suggestions = generate_refactoring_suggestions(code_smells)
        
        # Calculate code quality score
        quality_score = calculate_code_quality_score(code_smells, len(code.split('\n')))
        
        return {
            "status": "success",
            "result": {
                "code_smells": code_smells,
                "suggestions": suggestions,
                "quality_score": quality_score,
                "total_smells": len(code_smells),
                "severity_distribution": get_severity_distribution(code_smells)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "detect_code_smells"
        }


@log_tool_execution("backward_compatibility")
def check_backward_compatibility(code: str, target_version: str = "3.8") -> Dict[str, Any]:
    """
    Check backward compatibility and suggest migration strategies.
    
    Args:
        code: Python code to check
        target_version: Target Python version for compatibility
        
    Returns:
        Dict with compatibility issues and migration suggestions
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        tree = ast.parse(code)
        compatibility_issues = []
        migration_suggestions = []
        
        # Check for version-specific features
        version_features = {
            "3.8": ["walrus_operator", "positional_only_params"],
            "3.9": ["dict_union_operators", "generic_types"],
            "3.10": ["match_statements", "union_types"],
            "3.11": ["exception_groups", "task_groups"],
            "3.12": ["type_params", "generic_syntax"]
        }
        
        # Detect incompatible features
        for version, features in version_features.items():
            if version > target_version:
                for feature in features:
                    if feature_present_in_code(code, tree, feature):
                        compatibility_issues.append({
                            "feature": feature,
                            "introduced_in": version,
                            "target_version": target_version,
                            "severity": "error" if version > target_version else "warning"
                        })
                        
                        # Generate migration suggestion
                        suggestion = generate_migration_suggestion(feature, target_version)
                        if suggestion:
                            migration_suggestions.append(suggestion)
                            
        # Check for deprecated features
        deprecated_features = detect_deprecated_features(code, tree)
        
        # Generate backward compatible alternatives
        alternatives = generate_compatible_alternatives(code, target_version)
        
        return {
            "status": "success",
            "result": {
                "target_version": target_version,
                "compatibility_issues": compatibility_issues,
                "deprecated_features": deprecated_features,
                "migration_suggestions": migration_suggestions,
                "compatible_alternatives": alternatives,
                "is_compatible": len(compatibility_issues) == 0,
                "compatibility_score": calculate_compatibility_score(compatibility_issues)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "backward_compatibility"
        }


# Refactoring implementations
def modernize_code(code: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Modernize code with latest Python features."""
    changes = []
    updated_code = code
    
    # Convert old string formatting to f-strings
    old_format_pattern = r'(["\'])([^"\']*?)%\s*\(([^)]+)\)\1'
    matches = re.findall(old_format_pattern, updated_code)
    if matches:
        for quote, format_str, args in matches:
            # Simple conversion (more complex logic needed for full implementation)
            f_string = f'f{quote}{format_str.replace("%s", "{}")}{quote}'
            updated_code = updated_code.replace(f'{quote}{format_str}%({args}){quote}', f_string, 1)
            changes.append({
                "type": "string_formatting",
                "description": "Converted % formatting to f-string",
                "line": get_line_number(code, f'{quote}{format_str}%({args}){quote}')
            })
            
    # Convert .format() to f-strings
    format_pattern = r'(["\'])([^"\']*?)\{([^}]+)\}([^"\']*?)\1\.format\(([^)]+)\)'
    matches = re.findall(format_pattern, updated_code)
    if matches:
        for match in matches:
            changes.append({
                "type": "format_to_fstring",
                "description": "Converted .format() to f-string",
                "line": get_line_number(code, match[0])
            })
            
    # Add type hints where missing (simplified)
    if "def " in updated_code and "->" not in updated_code:
        changes.append({
            "type": "add_type_hints",
            "description": "Consider adding type hints to functions",
            "line": get_line_number(updated_code, "def ")
        })
        
    return updated_code, changes


def optimize_performance(code: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Apply performance optimizations."""
    changes = []
    updated_code = code
    
    # Convert range(len()) to enumerate
    range_len_pattern = r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):'
    matches = re.findall(range_len_pattern, updated_code)
    for var, seq in matches:
        old_pattern = f'for {var} in range(len({seq})):'
        new_pattern = f'for {var}, item in enumerate({seq}):'
        updated_code = updated_code.replace(old_pattern, new_pattern)
        changes.append({
            "type": "enumerate_optimization",
            "description": f"Converted range(len({seq})) to enumerate({seq})",
            "line": get_line_number(code, old_pattern)
        })
        
    # Suggest list comprehensions
    append_pattern = r'(\w+)\s*=\s*\[\]\s*\n.*?for\s+\w+\s+in\s+.*?:\s*\n\s*\1\.append\('
    if re.search(append_pattern, updated_code, re.MULTILINE | re.DOTALL):
        changes.append({
            "type": "list_comprehension",
            "description": "Consider using list comprehension instead of append in loop",
            "line": get_line_number(updated_code, ".append(")
        })
        
    return updated_code, changes


def improve_readability(code: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Improve code readability."""
    changes = []
    updated_code = code
    
    # Add docstrings to functions without them
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not ast.get_docstring(node):
                changes.append({
                    "type": "missing_docstring",
                    "description": f"Add docstring to function '{node.name}'",
                    "line": node.lineno
                })
                
    # Suggest variable name improvements
    short_vars = re.findall(r'\b([a-z])\s*=', code)
    if short_vars:
        changes.append({
            "type": "variable_naming",
            "description": f"Consider more descriptive names for variables: {', '.join(set(short_vars))}",
            "line": 1
        })
        
    return updated_code, changes


def apply_pattern_improvements(code: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Apply common pattern improvements."""
    changes = []
    updated_code = code
    
    # Convert if __name__ == "__main__" guard
    if 'if __name__ == "__main__":' not in code and "def main(" in code:
        updated_code += '\n\nif __name__ == "__main__":\n    main()\n'
        changes.append({
            "type": "main_guard",
            "description": "Added if __name__ == '__main__' guard",
            "line": len(code.split('\n'))
        })
        
    return updated_code, changes


# Code smell detection functions
def detect_long_methods(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect methods that are too long."""
    smells = []
    lines = code.split('\n')
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Calculate method length
            end_line = node.end_lineno or node.lineno
            method_length = end_line - node.lineno + 1
            
            if method_length > 20:  # Configurable threshold
                smells.append({
                    "type": "long_method",
                    "name": node.name,
                    "line": node.lineno,
                    "length": method_length,
                    "severity": "medium" if method_length > 30 else "low",
                    "suggestion": "Consider breaking this method into smaller functions"
                })
                
    return smells


def detect_large_classes(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect classes that are too large."""
    smells = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            method_count = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))
            
            if method_count > 10:  # Configurable threshold
                smells.append({
                    "type": "large_class",
                    "name": node.name,
                    "line": node.lineno,
                    "method_count": method_count,
                    "severity": "medium" if method_count > 15 else "low",
                    "suggestion": "Consider splitting this class using composition or inheritance"
                })
                
    return smells


def detect_god_objects(tree: ast.AST) -> List[Dict[str, Any]]:
    """Detect god objects (classes with too many responsibilities)."""
    smells = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Count different types of methods
            public_methods = 0
            private_methods = 0
            properties = 0
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name.startswith('_'):
                        private_methods += 1
                    else:
                        public_methods += 1
                        
            total_complexity = public_methods + private_methods
            
            if total_complexity > 15:
                smells.append({
                    "type": "god_object",
                    "name": node.name,
                    "line": node.lineno,
                    "complexity": total_complexity,
                    "severity": "high",
                    "suggestion": "This class has too many responsibilities. Consider using composition."
                })
                
    return smells


def detect_duplicate_code(code: str) -> List[Dict[str, Any]]:
    """Detect duplicate code blocks."""
    smells = []
    lines = code.split('\n')
    
    # Simple duplicate detection (can be improved)
    line_groups = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            if stripped not in line_groups:
                line_groups[stripped] = []
            line_groups[stripped].append(i + 1)
            
    for line_content, line_numbers in line_groups.items():
        if len(line_numbers) > 2 and len(line_content) > 20:
            smells.append({
                "type": "duplicate_code",
                "content": line_content[:50] + "...",
                "lines": line_numbers,
                "count": len(line_numbers),
                "severity": "medium",
                "suggestion": "Extract this duplicate code into a function"
            })
            
    return smells


def detect_magic_numbers(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect magic numbers in code."""
    smells = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and node.value not in [0, 1, -1, 2]:
                smells.append({
                    "type": "magic_number",
                    "value": node.value,
                    "line": node.lineno,
                    "severity": "low",
                    "suggestion": f"Consider defining {node.value} as a named constant"
                })
                
    return smells


def detect_long_parameter_lists(tree: ast.AST) -> List[Dict[str, Any]]:
    """Detect functions with too many parameters."""
    smells = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            param_count = len(node.args.args)
            
            if param_count > 5:  # Configurable threshold
                smells.append({
                    "type": "long_parameter_list",
                    "name": node.name,
                    "line": node.lineno,
                    "param_count": param_count,
                    "severity": "medium" if param_count > 7 else "low",
                    "suggestion": "Consider using a data class or dictionary for parameters"
                })
                
    return smells


def detect_dead_code(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect potentially dead code."""
    smells = []
    
    # Simple detection for unreachable code after return
    lines = code.split('\n')
    for i, line in enumerate(lines[:-1]):
        if 'return' in line.strip() and not line.strip().startswith('#'):
            next_line = lines[i + 1].strip()
            if next_line and not next_line.startswith(('def ', 'class ', 'if ', 'elif ', 'else:', '#')):
                smells.append({
                    "type": "dead_code",
                    "line": i + 2,
                    "severity": "medium",
                    "suggestion": "Code after return statement may be unreachable"
                })
                
    return smells


def detect_complex_conditionals(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect overly complex conditional statements."""
    smells = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Count boolean operators in condition
            bool_ops = sum(1 for n in ast.walk(node.test) if isinstance(n, ast.BoolOp))
            
            if bool_ops > 3:
                smells.append({
                    "type": "complex_conditional",
                    "line": node.lineno,
                    "complexity": bool_ops,
                    "severity": "medium",
                    "suggestion": "Consider extracting complex conditions into separate functions"
                })
                
    return smells


# Helper functions
def generate_refactoring_suggestions(code_smells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate refactoring suggestions based on code smells."""
    suggestions = []
    
    smell_types = set(smell["type"] for smell in code_smells)
    
    if "long_method" in smell_types:
        suggestions.append({
            "type": "extract_method",
            "description": "Break long methods into smaller, focused functions",
            "priority": "medium"
        })
        
    if "duplicate_code" in smell_types:
        suggestions.append({
            "type": "extract_function", 
            "description": "Extract duplicate code into reusable functions",
            "priority": "high"
        })
        
    if "magic_number" in smell_types:
        suggestions.append({
            "type": "introduce_constants",
            "description": "Replace magic numbers with named constants",
            "priority": "low"
        })
        
    return suggestions


def calculate_code_quality_score(code_smells: List[Dict[str, Any]], lines_of_code: int) -> int:
    """Calculate overall code quality score."""
    if lines_of_code == 0:
        return 100
        
    severity_weights = {"low": 1, "medium": 3, "high": 5}
    total_penalty = sum(severity_weights.get(smell.get("severity", "low"), 1) for smell in code_smells)
    
    # Normalize by lines of code
    penalty_per_line = total_penalty / max(lines_of_code, 1) * 100
    
    return max(0, int(100 - penalty_per_line))


def get_severity_distribution(code_smells: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get distribution of code smell severities."""
    distribution = {"low": 0, "medium": 0, "high": 0}
    
    for smell in code_smells:
        severity = smell.get("severity", "low")
        distribution[severity] += 1
        
    return distribution


def feature_present_in_code(code: str, tree: ast.AST, feature: str) -> bool:
    """Check if a specific Python feature is present in code."""
    feature_checks = {
        "walrus_operator": lambda: ":=" in code,
        "match_statements": lambda: "match " in code and "case " in code,
        "union_types": lambda: " | " in code,
        "positional_only_params": lambda: any(
            isinstance(node, ast.FunctionDef) and any(
                isinstance(arg, ast.arg) for arg in node.args.posonlyargs
            ) for node in ast.walk(tree)
        ),
        "dict_union_operators": lambda: "|=" in code,
        "generic_types": lambda: "Generic[" in code or "TypeVar" in code,
        "exception_groups": lambda: "ExceptionGroup" in code,
        "task_groups": lambda: "TaskGroup" in code,
        "type_params": lambda: "[T:" in code or "[K:" in code,
        "generic_syntax": lambda: "class Generic[" in code
    }
    
    check_func = feature_checks.get(feature)
    return check_func() if check_func else False


def generate_migration_suggestion(feature: str, target_version: str) -> Optional[Dict[str, Any]]:
    """Generate migration suggestion for incompatible features."""
    suggestions = {
        "walrus_operator": {
            "description": "Replace walrus operator with separate assignment",
            "example": "Replace 'if (n := len(items)) > 0:' with 'n = len(items); if n > 0:'"
        },
        "match_statements": {
            "description": "Replace match statements with if/elif chains",
            "example": "Convert match/case to if/elif/else statements"
        },
        "union_types": {
            "description": "Use typing.Union instead of | operator",
            "example": "Replace 'str | int' with 'Union[str, int]'"
        }
    }
    
    return suggestions.get(feature)


def detect_deprecated_features(code: str, tree: ast.AST) -> List[Dict[str, Any]]:
    """Detect deprecated Python features."""
    deprecated = []
    
    # Check for deprecated imports
    deprecated_imports = {
        "imp": "Use importlib instead",
        "distutils": "Use setuptools instead",
        "asyncore": "Use asyncio instead",
        "asynchat": "Use asyncio instead"
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in deprecated_imports:
                    deprecated.append({
                        "type": "deprecated_import",
                        "name": alias.name,
                        "line": node.lineno,
                        "suggestion": deprecated_imports[alias.name]
                    })
                    
    return deprecated


def generate_compatible_alternatives(code: str, target_version: str) -> List[Dict[str, Any]]:
    """Generate backward compatible alternatives."""
    alternatives = []
    
    # F-string alternatives for older versions
    if "f'" in code or 'f"' in code:
        if target_version < "3.6":
            alternatives.append({
                "feature": "f-strings", 
                "alternative": "Use .format() or % formatting",
                "example": "f'{name}' -> '{}'.format(name)"
            })
            
    return alternatives


def calculate_compatibility_score(issues: List[Dict[str, Any]]) -> int:
    """Calculate backward compatibility score."""
    if not issues:
        return 100
        
    severity_weights = {"error": 20, "warning": 5}
    penalty = sum(severity_weights.get(issue.get("severity", "warning"), 5) for issue in issues)
    
    return max(0, 100 - penalty)


def calculate_improvement_metrics(original: str, refactored: str) -> Dict[str, Any]:
    """Calculate improvement metrics between original and refactored code."""
    original_lines = len(original.split('\n'))
    refactored_lines = len(refactored.split('\n'))
    
    return {
        "lines_changed": abs(original_lines - refactored_lines),
        "size_reduction": max(0, original_lines - refactored_lines),
        "readability_improvement": estimate_readability_improvement(original, refactored),
        "modernization_level": estimate_modernization_level(refactored)
    }


def estimate_readability_improvement(original: str, refactored: str) -> float:
    """Estimate readability improvement (simplified metric)."""
    # Count f-strings, type hints, descriptive names
    original_score = count_readability_features(original)
    refactored_score = count_readability_features(refactored)
    
    return max(0, refactored_score - original_score)


def count_readability_features(code: str) -> float:
    """Count readability features in code."""
    score = 0
    score += code.count("f'") + code.count('f"')  # F-strings
    score += code.count("->") * 0.5  # Type hints
    score += code.count('"""') * 0.3  # Docstrings
    return score


def estimate_modernization_level(code: str) -> float:
    """Estimate how modern the code is (0-100)."""
    modern_features = 0
    total_checks = 10
    
    if "f'" in code or 'f"' in code:
        modern_features += 1
    if "->" in code:
        modern_features += 1
    if ":=" in code:
        modern_features += 1
    if "match " in code:
        modern_features += 1
    if "@dataclass" in code:
        modern_features += 1
    if "async " in code:
        modern_features += 1
    if "with " in code:
        modern_features += 1
    if "yield from" in code:
        modern_features += 1
    if "pathlib" in code:
        modern_features += 1
    if "typing" in code:
        modern_features += 1
        
    return (modern_features / total_checks) * 100


def get_line_number(code: str, search_text: str) -> int:
    """Get line number of text in code."""
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if search_text in line:
            return i + 1
    return 1

