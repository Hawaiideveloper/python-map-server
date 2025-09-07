"""
Advanced testing and debugging tools for expert-level Python development.

This module provides comprehensive testing strategies, debugging techniques,
and quality assurance tools that a 30-year Python veteran would use.
"""

import ast
import inspect
import pdb
import re
import subprocess
import tempfile
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.logging import log_tool_execution
from ..utils.security import validate_code_safety


@log_tool_execution("generate_tests")
def generate_comprehensive_tests(code: str, test_framework: str = "pytest") -> Dict[str, Any]:
    """
    Generate comprehensive test suite for given code.
    
    Args:
        code: Python code to generate tests for
        test_framework: Testing framework (pytest, unittest, doctest)
        
    Returns:
        Dict with generated test code and testing strategy
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        tree = ast.parse(code)
        
        # Analyze code structure
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "lineno": node.lineno,
                    "docstring": ast.get_docstring(node),
                    "returns_value": has_return_statement(node),
                    "complexity": calculate_function_complexity(node)
                })
            elif isinstance(node, ast.ClassDef):
                methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
                classes.append({
                    "name": node.name,
                    "methods": methods,
                    "lineno": node.lineno,
                    "docstring": ast.get_docstring(node)
                })
        
        # Generate test code
        test_code = generate_test_code(functions, classes, test_framework)
        
        # Generate testing strategy
        strategy = generate_testing_strategy(functions, classes, code)
        
        # Generate test data and edge cases
        test_data = generate_test_data(functions, classes)
        
        return {
            "status": "success",
            "result": {
                "test_code": test_code,
                "test_framework": test_framework,
                "testing_strategy": strategy,
                "test_data_suggestions": test_data,
                "coverage_targets": generate_coverage_targets(functions, classes),
                "functions_analyzed": len(functions),
                "classes_analyzed": len(classes)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "generate_tests"
        }


@log_tool_execution("debug_analysis")
def analyze_debugging_opportunities(code: str, error_context: str = "") -> Dict[str, Any]:
    """
    Analyze code for debugging opportunities and suggest debugging strategies.
    
    Args:
        code: Python code to analyze
        error_context: Any error messages or context
        
    Returns:
        Dict with debugging analysis and recommendations
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        tree = ast.parse(code)
        
        # Debugging analysis
        debug_points = identify_debug_points(tree, code)
        logging_opportunities = identify_logging_opportunities(tree, code)
        assertion_suggestions = suggest_assertions(tree, code)
        error_handling_gaps = identify_error_handling_gaps(tree, code)
        
        # Generate debugging strategies
        strategies = generate_debugging_strategies(debug_points, error_context)
        
        # Suggest debugging tools
        tool_recommendations = suggest_debugging_tools(code, error_context)
        
        return {
            "status": "success",
            "result": {
                "debug_points": debug_points,
                "logging_opportunities": logging_opportunities,
                "assertion_suggestions": assertion_suggestions,
                "error_handling_gaps": error_handling_gaps,
                "debugging_strategies": strategies,
                "tool_recommendations": tool_recommendations,
                "expert_tips": generate_expert_debugging_tips(code, error_context)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "debug_analysis"
        }


@log_tool_execution("test_quality_analysis")
def analyze_test_quality(test_code: str) -> Dict[str, Any]:
    """
    Analyze quality of existing test code.
    
    Args:
        test_code: Test code to analyze
        
    Returns:
        Dict with test quality analysis
    """
    try:
        if not test_code:
            raise ValueError("test_code is required")
            
        tree = ast.parse(test_code)
        
        # Test quality metrics
        test_functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
        
        quality_metrics = {
            "test_count": len(test_functions),
            "assertion_count": count_assertions(tree),
            "setup_teardown": has_setup_teardown(tree),
            "parametrized_tests": count_parametrized_tests(tree, test_code),
            "mock_usage": count_mock_usage(tree, test_code),
            "fixture_usage": count_fixture_usage(tree, test_code),
            "test_organization": analyze_test_organization(tree),
            "edge_case_coverage": analyze_edge_case_coverage(tree, test_code)
        }
        
        # Calculate quality score
        quality_score = calculate_test_quality_score(quality_metrics)
        
        # Generate improvement suggestions
        improvements = suggest_test_improvements(quality_metrics, test_code)
        
        return {
            "status": "success",
            "result": {
                "quality_metrics": quality_metrics,
                "quality_score": quality_score,
                "improvement_suggestions": improvements,
                "expert_recommendations": generate_test_expert_recommendations(quality_metrics)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "test_quality_analysis"
        }


@log_tool_execution("mutation_testing")
def suggest_mutation_testing(code: str, test_code: str) -> Dict[str, Any]:
    """
    Suggest mutation testing strategies to improve test quality.
    
    Args:
        code: Source code
        test_code: Test code
        
    Returns:
        Dict with mutation testing suggestions
    """
    try:
        if not code or not test_code:
            raise ValueError("Both code and test_code are required")
            
        # Analyze code for mutation opportunities
        mutations = identify_mutation_opportunities(code)
        
        # Suggest specific mutations
        mutation_suggestions = generate_mutation_suggestions(mutations)
        
        # Estimate test effectiveness
        effectiveness = estimate_test_effectiveness(code, test_code)
        
        return {
            "status": "success",
            "result": {
                "mutation_opportunities": mutations,
                "mutation_suggestions": mutation_suggestions,
                "test_effectiveness": effectiveness,
                "tools_recommended": ["mutmut", "cosmic-ray", "mutpy"],
                "expert_guidance": generate_mutation_testing_guidance()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "mutation_testing"
        }


@log_tool_execution("property_based_testing")
def suggest_property_based_tests(code: str) -> Dict[str, Any]:
    """
    Suggest property-based testing strategies using Hypothesis.
    
    Args:
        code: Python code to analyze
        
    Returns:
        Dict with property-based testing suggestions
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        tree = ast.parse(code)
        
        # Identify functions suitable for property-based testing
        suitable_functions = identify_property_testable_functions(tree, code)
        
        # Generate property-based test examples
        property_tests = generate_property_tests(suitable_functions)
        
        # Suggest invariants and properties
        properties = suggest_function_properties(suitable_functions)
        
        return {
            "status": "success",
            "result": {
                "suitable_functions": suitable_functions,
                "property_tests": property_tests,
                "suggested_properties": properties,
                "hypothesis_strategies": suggest_hypothesis_strategies(suitable_functions),
                "expert_insights": generate_property_testing_insights()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "property_based_testing"
        }


# Helper functions for test generation
def has_return_statement(node: ast.FunctionDef) -> bool:
    """Check if function has return statement."""
    for item in ast.walk(node):
        if isinstance(item, ast.Return):
            return True
    return False


def calculate_function_complexity(node: ast.FunctionDef) -> int:
    """Calculate cyclomatic complexity of function."""
    complexity = 1
    for item in ast.walk(node):
        if isinstance(item, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            complexity += 1
        elif isinstance(item, ast.BoolOp):
            complexity += len(item.values) - 1
    return complexity


def generate_test_code(functions: List[Dict], classes: List[Dict], framework: str) -> str:
    """Generate test code based on analyzed functions and classes."""
    if framework == "pytest":
        return generate_pytest_code(functions, classes)
    elif framework == "unittest":
        return generate_unittest_code(functions, classes)
    else:
        return generate_doctest_code(functions, classes)


def generate_pytest_code(functions: List[Dict], classes: List[Dict]) -> str:
    """Generate pytest test code."""
    test_code = """import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add source directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
    
    # Generate function tests
    for func in functions:
        test_code += f"""
def test_{func['name']}_basic():
    \"\"\"Test basic functionality of {func['name']}.\"\"\"
    # TODO: Implement test
    pass

def test_{func['name']}_edge_cases():
    \"\"\"Test edge cases for {func['name']}.\"\"\"
    # TODO: Test with empty inputs, None, extreme values
    pass

def test_{func['name']}_error_conditions():
    \"\"\"Test error conditions for {func['name']}.\"\"\"
    # TODO: Test invalid inputs, error handling
    pass
"""
    
    # Generate class tests
    for cls in classes:
        test_code += f"""
class Test{cls['name']}:
    \"\"\"Test suite for {cls['name']} class.\"\"\"
    
    @pytest.fixture
    def {cls['name'].lower()}_instance(self):
        \"\"\"Create instance for testing.\"\"\"
        return {cls['name']}()
    
    def test_initialization(self, {cls['name'].lower()}_instance):
        \"\"\"Test class initialization.\"\"\"
        assert isinstance({cls['name'].lower()}_instance, {cls['name']})
"""
        
        for method in cls['methods']:
            if not method.startswith('_'):  # Skip private methods
                test_code += f"""
    def test_{method}(self, {cls['name'].lower()}_instance):
        \"\"\"Test {method} method.\"\"\"
        # TODO: Implement test
        pass
"""
    
    return test_code


def generate_unittest_code(functions: List[Dict], classes: List[Dict]) -> str:
    """Generate unittest test code."""
    test_code = """import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add source directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
    
    # Generate test class
    test_code += """class TestSuite(unittest.TestCase):
    \"\"\"Comprehensive test suite.\"\"\"
    
    def setUp(self):
        \"\"\"Set up test fixtures.\"\"\"
        pass
    
    def tearDown(self):
        \"\"\"Clean up after tests.\"\"\"
        pass
"""
    
    # Generate function tests
    for func in functions:
        test_code += f"""
    def test_{func['name']}_basic(self):
        \"\"\"Test basic functionality of {func['name']}.\"\"\"
        # TODO: Implement test
        pass
    
    def test_{func['name']}_edge_cases(self):
        \"\"\"Test edge cases for {func['name']}.\"\"\"
        # TODO: Test with empty inputs, None, extreme values
        pass
"""
    
    test_code += """

if __name__ == '__main__':
    unittest.main()
"""
    
    return test_code


def generate_doctest_code(functions: List[Dict], classes: List[Dict]) -> str:
    """Generate doctest examples."""
    doctest_code = """# Doctest examples to add to your functions:

"""
    
    for func in functions:
        doctest_code += f"""
# For function {func['name']}:
def {func['name']}({', '.join(func['args'])}):
    \"\"\"
    {func['name']} function description.
    
    Examples:
    >>> {func['name']}(test_input)
    expected_output
    
    >>> {func['name']}(edge_case_input)
    edge_case_output
    
    >>> {func['name']}(invalid_input)
    Traceback (most recent call last):
        ...
    ValueError: Invalid input
    \"\"\"
    pass
"""
    
    return doctest_code


def generate_testing_strategy(functions: List[Dict], classes: List[Dict], code: str) -> Dict[str, Any]:
    """Generate comprehensive testing strategy."""
    strategy = {
        "unit_tests": {
            "target_coverage": "95%",
            "focus_areas": ["business logic", "edge cases", "error handling"],
            "test_count_estimate": len(functions) * 3 + len(classes) * 2
        },
        "integration_tests": {
            "recommended": len(classes) > 1 or "import" in code,
            "focus_areas": ["component interaction", "data flow"]
        },
        "property_tests": {
            "suitable_functions": [f["name"] for f in functions if f["complexity"] > 3],
            "recommended_tool": "Hypothesis"
        },
        "mutation_tests": {
            "recommended": len(functions) > 5,
            "estimated_mutations": len(functions) * 10
        }
    }
    
    return strategy


def generate_test_data(functions: List[Dict], classes: List[Dict]) -> Dict[str, Any]:
    """Generate test data suggestions."""
    return {
        "common_edge_cases": [
            "Empty collections",
            "None values", 
            "Zero and negative numbers",
            "Very large numbers",
            "Empty strings",
            "Unicode strings",
            "Boundary values"
        ],
        "data_generators": {
            "strings": ["'test'", "''", "'unicode: 🐍'", "'very_long_string' * 1000"],
            "numbers": ["0", "-1", "1", "sys.maxsize", "float('inf')", "float('nan')"],
            "collections": ["[]", "[1]", "list(range(1000))", "{}", "{'key': 'value'}"]
        },
        "mock_scenarios": [
            "External API calls",
            "File system operations", 
            "Database connections",
            "Network requests",
            "Time-dependent operations"
        ]
    }


def generate_coverage_targets(functions: List[Dict], classes: List[Dict]) -> Dict[str, Any]:
    """Generate coverage targets."""
    return {
        "line_coverage": "95%",
        "branch_coverage": "90%",
        "function_coverage": "100%",
        "class_coverage": "100%",
        "critical_paths": [f["name"] for f in functions if f["complexity"] > 5],
        "coverage_exclusions": ["__init__.py", "setup.py", "tests/"]
    }


# Helper functions for debugging analysis
def identify_debug_points(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Identify key debugging points in code."""
    debug_points = []
    
    # Complex conditionals
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            complexity = count_boolean_operators(node.test)
            if complexity > 2:
                debug_points.append({
                    "type": "complex_conditional",
                    "line": node.lineno,
                    "complexity": complexity,
                    "suggestion": "Add logging before and after condition"
                })
    
    # Loops with complex logic
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            if count_nested_statements(node) > 5:
                debug_points.append({
                    "type": "complex_loop",
                    "line": node.lineno,
                    "suggestion": "Add iteration logging and break conditions"
                })
    
    # Function calls that might fail
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                debug_points.append({
                    "type": "method_call",
                    "line": getattr(node, 'lineno', 0),
                    "suggestion": "Consider try-catch around external calls"
                })
    
    return debug_points


def identify_logging_opportunities(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Identify where logging should be added."""
    opportunities = []
    
    # Function entry/exit points
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not has_logging_in_function(node):
                opportunities.append({
                    "type": "function_logging",
                    "function": node.name,
                    "line": node.lineno,
                    "suggestion": "Add entry/exit logging with parameters and return values"
                })
    
    # Exception handling blocks
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            opportunities.append({
                "type": "exception_logging",
                "line": node.lineno,
                "suggestion": "Log exception details with context"
            })
    
    # State changes
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if is_important_state_change(node):
                opportunities.append({
                    "type": "state_change",
                    "line": node.lineno,
                    "suggestion": "Log state changes for debugging"
                })
    
    return opportunities


def suggest_assertions(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Suggest where assertions should be added."""
    suggestions = []
    
    # Function preconditions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not has_assertions_in_function(node):
                suggestions.append({
                    "type": "precondition",
                    "function": node.name,
                    "line": node.lineno,
                    "suggestion": "Add assertions for parameter validation"
                })
    
    # Postconditions
    for node in ast.walk(tree):
        if isinstance(node, ast.Return):
            suggestions.append({
                "type": "postcondition",
                "line": node.lineno,
                "suggestion": "Add assertion to validate return value"
            })
    
    return suggestions


def identify_error_handling_gaps(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Identify gaps in error handling."""
    gaps = []
    
    # Functions without try-catch
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not has_exception_handling(node):
                gaps.append({
                    "type": "missing_exception_handling",
                    "function": node.name,
                    "line": node.lineno,
                    "severity": "medium"
                })
    
    # File operations without error handling
    if any(call in code for call in ["open(", "file(", "read(", "write("]):
        gaps.append({
            "type": "file_operations",
            "severity": "high",
            "suggestion": "Wrap file operations in try-catch blocks"
        })
    
    return gaps


def generate_debugging_strategies(debug_points: List[Dict], error_context: str) -> List[Dict[str, Any]]:
    """Generate specific debugging strategies."""
    strategies = []
    
    if error_context:
        strategies.append({
            "strategy": "error_focused_debugging",
            "description": "Focus debugging on error context",
            "steps": [
                "Add logging around the error point",
                "Check input values leading to error",
                "Verify assumptions about data types",
                "Test with minimal reproduction case"
            ]
        })
    
    if len(debug_points) > 5:
        strategies.append({
            "strategy": "systematic_logging",
            "description": "Add systematic logging throughout complex code",
            "steps": [
                "Add function entry/exit logging",
                "Log all parameter values",
                "Log intermediate calculations",
                "Use structured logging with correlation IDs"
            ]
        })
    
    strategies.append({
        "strategy": "interactive_debugging",
        "description": "Use interactive debugger for complex issues",
        "tools": ["pdb", "ipdb", "pudb", "IDE debugger"],
        "steps": [
            "Set breakpoints at critical points",
            "Inspect variable states",
            "Step through code execution",
            "Use conditional breakpoints"
        ]
    })
    
    return strategies


def suggest_debugging_tools(code: str, error_context: str) -> List[Dict[str, Any]]:
    """Suggest appropriate debugging tools."""
    tools = []
    
    tools.append({
        "tool": "pdb",
        "use_case": "Interactive debugging",
        "command": "python -m pdb script.py",
        "benefits": ["Step-by-step execution", "Variable inspection", "Call stack analysis"]
    })
    
    if "async" in code:
        tools.append({
            "tool": "aiomonitor",
            "use_case": "Async debugging",
            "command": "pip install aiomonitor",
            "benefits": ["Async task monitoring", "Event loop inspection"]
        })
    
    if "memory" in error_context.lower():
        tools.append({
            "tool": "memory_profiler",
            "use_case": "Memory debugging",
            "command": "pip install memory-profiler",
            "benefits": ["Memory usage tracking", "Memory leak detection"]
        })
    
    tools.append({
        "tool": "logging",
        "use_case": "Production debugging",
        "setup": "import logging; logging.basicConfig(level=logging.DEBUG)",
        "benefits": ["Permanent debugging info", "Configurable verbosity", "Production-safe"]
    })
    
    return tools


def generate_expert_debugging_tips(code: str, error_context: str) -> List[str]:
    """Generate expert debugging tips."""
    tips = [
        "Always reproduce the bug in the simplest possible case",
        "Use binary search to isolate the problem area",
        "Log the 'path not taken' to understand control flow",
        "Print/log the types of variables, not just values",
        "Use assertions to encode your assumptions",
        "Debug with the same conditions as production",
        "Keep a debugging log to avoid repeating investigations",
        "Test your fix with edge cases, not just the reported bug"
    ]
    
    if "async" in code:
        tips.extend([
            "Async bugs often involve timing - add delays to test",
            "Check for blocking operations in async code",
            "Monitor the event loop for deadlocks"
        ])
    
    if "class" in code:
        tips.extend([
            "Check object lifecycle and state mutations",
            "Verify inheritance and method resolution order",
            "Test with different object instances"
        ])
    
    return tips


# Helper functions for test quality analysis
def count_assertions(tree: ast.AST) -> int:
    """Count assertion statements in test code."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            count += 1
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr.startswith('assert'):
                count += 1
    return count


def has_setup_teardown(tree: ast.AST) -> bool:
    """Check if test has setup/teardown methods."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name in ['setUp', 'tearDown', 'setup_method', 'teardown_method']:
                return True
    return False


def count_parametrized_tests(tree: ast.AST, code: str) -> int:
    """Count parametrized tests."""
    return code.count('@pytest.mark.parametrize') + code.count('@parameterized')


def count_mock_usage(tree: ast.AST, code: str) -> int:
    """Count mock usage in tests."""
    return code.count('Mock') + code.count('patch') + code.count('mock')


def count_fixture_usage(tree: ast.AST, code: str) -> int:
    """Count fixture usage."""
    return code.count('@pytest.fixture') + code.count('@fixture')


def analyze_test_organization(tree: ast.AST) -> Dict[str, Any]:
    """Analyze test organization."""
    test_classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name.startswith('Test')]
    test_functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
    
    return {
        "test_classes": len(test_classes),
        "test_functions": len(test_functions),
        "organization": "class-based" if test_classes else "function-based"
    }


def analyze_edge_case_coverage(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze edge case coverage in tests."""
    edge_case_indicators = [
        'empty', 'none', 'null', 'zero', 'negative', 'large', 'boundary',
        'invalid', 'error', 'exception', 'edge', 'corner'
    ]
    
    edge_case_tests = sum(1 for indicator in edge_case_indicators if indicator in code.lower())
    
    return {
        "edge_case_indicators": edge_case_tests,
        "coverage_level": "good" if edge_case_tests > 5 else "fair" if edge_case_tests > 2 else "poor"
    }


def calculate_test_quality_score(metrics: Dict[str, Any]) -> int:
    """Calculate overall test quality score."""
    score = 0
    
    # Test count
    if metrics["test_count"] > 10:
        score += 20
    elif metrics["test_count"] > 5:
        score += 15
    elif metrics["test_count"] > 0:
        score += 10
    
    # Assertions
    if metrics["assertion_count"] > metrics["test_count"] * 2:
        score += 20
    elif metrics["assertion_count"] > metrics["test_count"]:
        score += 15
    elif metrics["assertion_count"] > 0:
        score += 10
    
    # Setup/teardown
    if metrics["setup_teardown"]:
        score += 15
    
    # Advanced features
    if metrics["parametrized_tests"] > 0:
        score += 10
    if metrics["mock_usage"] > 0:
        score += 10
    if metrics["fixture_usage"] > 0:
        score += 10
    
    # Edge case coverage
    if metrics["edge_case_coverage"]["coverage_level"] == "good":
        score += 15
    elif metrics["edge_case_coverage"]["coverage_level"] == "fair":
        score += 10
    
    return min(100, score)


def suggest_test_improvements(metrics: Dict[str, Any], test_code: str) -> List[Dict[str, Any]]:
    """Suggest improvements to test code."""
    improvements = []
    
    if metrics["test_count"] < 5:
        improvements.append({
            "category": "coverage",
            "priority": "high",
            "suggestion": "Add more test cases to improve coverage",
            "details": "Aim for at least 3 tests per function: happy path, edge cases, error conditions"
        })
    
    if metrics["assertion_count"] < metrics["test_count"]:
        improvements.append({
            "category": "assertions",
            "priority": "high",
            "suggestion": "Add more assertions per test",
            "details": "Each test should have at least one meaningful assertion"
        })
    
    if not metrics["setup_teardown"]:
        improvements.append({
            "category": "organization",
            "priority": "medium",
            "suggestion": "Add setup and teardown methods",
            "details": "Use fixtures or setup/teardown for test data preparation"
        })
    
    if metrics["parametrized_tests"] == 0:
        improvements.append({
            "category": "efficiency",
            "priority": "medium",
            "suggestion": "Use parametrized tests for similar test cases",
            "details": "Reduce code duplication with @pytest.mark.parametrize"
        })
    
    return improvements


def generate_test_expert_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generate expert recommendations for testing."""
    recommendations = [
        "Follow the AAA pattern: Arrange, Act, Assert",
        "Test behavior, not implementation details",
        "Use descriptive test names that explain the scenario",
        "Keep tests simple and focused on one thing",
        "Use test doubles (mocks/stubs) for external dependencies",
        "Test edge cases and error conditions thoroughly",
        "Maintain test code quality like production code"
    ]
    
    if metrics["test_count"] > 20:
        recommendations.extend([
            "Consider test categorization (unit, integration, e2e)",
            "Implement test parallelization for faster execution",
            "Use test data builders for complex test scenarios"
        ])
    
    return recommendations


# Additional helper functions (simplified implementations)
def count_boolean_operators(node: ast.expr) -> int:
    """Count boolean operators in expression."""
    count = 0
    for item in ast.walk(node):
        if isinstance(item, ast.BoolOp):
            count += len(item.values) - 1
    return count


def count_nested_statements(node: ast.stmt) -> int:
    """Count nested statements in a node."""
    return len([item for item in ast.walk(node) if isinstance(item, ast.stmt)])


def has_logging_in_function(node: ast.FunctionDef) -> bool:
    """Check if function has logging statements."""
    for item in ast.walk(node):
        if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute):
            if item.func.attr in ['debug', 'info', 'warning', 'error', 'critical']:
                return True
    return False


def is_important_state_change(node: ast.Assign) -> bool:
    """Check if assignment represents important state change."""
    # Simplified heuristic
    return isinstance(node.targets[0], ast.Attribute)


def has_assertions_in_function(node: ast.FunctionDef) -> bool:
    """Check if function has assertion statements."""
    for item in ast.walk(node):
        if isinstance(item, ast.Assert):
            return True
    return False


def has_exception_handling(node: ast.FunctionDef) -> bool:
    """Check if function has exception handling."""
    for item in ast.walk(node):
        if isinstance(item, ast.Try):
            return True
    return False


# Mutation testing functions
def identify_mutation_opportunities(code: str) -> List[Dict[str, Any]]:
    """Identify opportunities for mutation testing."""
    opportunities = []
    
    # Arithmetic operators
    operators = ['+', '-', '*', '/', '//', '%', '**']
    for op in operators:
        if op in code:
            opportunities.append({
                "type": "arithmetic_operator",
                "operator": op,
                "mutation_examples": f"Change {op} to other arithmetic operators"
            })
    
    # Comparison operators
    comparisons = ['==', '!=', '<', '>', '<=', '>=']
    for comp in comparisons:
        if comp in code:
            opportunities.append({
                "type": "comparison_operator",
                "operator": comp,
                "mutation_examples": f"Change {comp} to other comparison operators"
            })
    
    # Boolean values
    if 'True' in code or 'False' in code:
        opportunities.append({
            "type": "boolean_literal",
            "mutation_examples": "Flip True to False and vice versa"
        })
    
    return opportunities


def generate_mutation_suggestions(mutations: List[Dict]) -> List[Dict[str, Any]]:
    """Generate specific mutation testing suggestions."""
    suggestions = []
    
    suggestions.append({
        "tool": "mutmut",
        "installation": "pip install mutmut",
        "usage": "mutmut run",
        "benefits": ["Simple to use", "Good Python support", "Clear reporting"]
    })
    
    suggestions.append({
        "strategy": "start_small",
        "description": "Begin with small functions and high test coverage",
        "steps": [
            "Choose functions with >90% test coverage",
            "Run mutations on critical business logic first",
            "Analyze surviving mutants to improve tests"
        ]
    })
    
    return suggestions


def estimate_test_effectiveness(code: str, test_code: str) -> Dict[str, Any]:
    """Estimate test effectiveness for mutation testing."""
    # Simplified estimation
    code_lines = len([line for line in code.split('\n') if line.strip()])
    test_lines = len([line for line in test_code.split('\n') if line.strip()])
    
    ratio = test_lines / code_lines if code_lines > 0 else 0
    
    effectiveness = "high" if ratio > 1.5 else "medium" if ratio > 0.8 else "low"
    
    return {
        "test_to_code_ratio": ratio,
        "effectiveness_estimate": effectiveness,
        "expected_mutation_score": "80-90%" if effectiveness == "high" else "60-80%" if effectiveness == "medium" else "40-60%"
    }


def generate_mutation_testing_guidance() -> List[str]:
    """Generate expert guidance for mutation testing."""
    return [
        "Start with high test coverage before mutation testing",
        "Focus on critical business logic and complex algorithms",
        "Aim for mutation score of 80% or higher",
        "Analyze surviving mutants to find test gaps",
        "Don't aim for 100% mutation score - some mutants are equivalent",
        "Use mutation testing to validate test quality, not just coverage",
        "Integrate mutation testing into CI/CD for important modules"
    ]


# Property-based testing functions
def identify_property_testable_functions(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Identify functions suitable for property-based testing."""
    suitable = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Functions with clear input/output relationships
            if (has_return_statement(node) and 
                len(node.args.args) > 0 and 
                not node.name.startswith('_')):
                
                suitable.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "complexity": calculate_function_complexity(node),
                    "suitability": assess_property_suitability(node, code)
                })
    
    return suitable


def assess_property_suitability(node: ast.FunctionDef, code: str) -> str:
    """Assess how suitable a function is for property-based testing."""
    # Functions with mathematical properties
    if any(word in node.name.lower() for word in ['sort', 'reverse', 'filter', 'map']):
        return "high"
    
    # Functions with clear invariants
    if any(word in node.name.lower() for word in ['validate', 'check', 'verify']):
        return "medium"
    
    return "low"


def generate_property_tests(functions: List[Dict]) -> List[Dict[str, Any]]:
    """Generate property-based test examples."""
    property_tests = []
    
    for func in functions:
        if func["suitability"] in ["high", "medium"]:
            property_tests.append({
                "function": func["name"],
                "test_example": f"""
from hypothesis import given, strategies as st

@given(st.{get_strategy_for_function(func)})
def test_{func['name']}_properties(input_data):
    result = {func['name']}(input_data)
    
    # Property: function should not crash
    assert result is not None
    
    # Add more specific properties based on function behavior
    # Example: if it's a sorting function
    # assert len(result) == len(input_data)
    # assert all(a <= b for a, b in zip(result, result[1:]))
""",
                "properties_to_test": suggest_properties_for_function(func)
            })
    
    return property_tests


def get_strategy_for_function(func: Dict) -> str:
    """Get appropriate Hypothesis strategy for function."""
    if "sort" in func["name"].lower():
        return "lists(st.integers())"
    elif "string" in func["name"].lower():
        return "text()"
    elif "number" in func["name"].lower():
        return "integers()"
    else:
        return "one_of(st.integers(), st.text(), st.lists(st.integers()))"


def suggest_properties_for_function(func: Dict) -> List[str]:
    """Suggest properties to test for a function."""
    common_properties = [
        "Function should not raise unexpected exceptions",
        "Output type should be consistent",
        "Function should be deterministic (same input → same output)"
    ]
    
    if "sort" in func["name"].lower():
        common_properties.extend([
            "Output length should equal input length",
            "Output should be sorted",
            "All input elements should be in output"
        ])
    elif "reverse" in func["name"].lower():
        common_properties.extend([
            "Reversing twice should return original",
            "Length should be preserved"
        ])
    
    return common_properties


def suggest_function_properties(functions: List[Dict]) -> Dict[str, List[str]]:
    """Suggest general properties for functions."""
    return {
        "mathematical_properties": [
            "Associativity: f(f(a, b), c) == f(a, f(b, c))",
            "Commutativity: f(a, b) == f(b, a)",
            "Identity: f(a, identity) == a",
            "Idempotence: f(f(a)) == f(a)"
        ],
        "invariants": [
            "Input constraints should be preserved",
            "Output should satisfy postconditions",
            "Function should maintain object invariants"
        ],
        "metamorphic_properties": [
            "Changing input in specific ways should change output predictably",
            "Multiple equivalent inputs should produce same output",
            "Function composition should behave predictably"
        ]
    }


def suggest_hypothesis_strategies(functions: List[Dict]) -> Dict[str, str]:
    """Suggest Hypothesis strategies for different data types."""
    return {
        "integers": "st.integers(min_value=-1000, max_value=1000)",
        "floats": "st.floats(allow_nan=False, allow_infinity=False)",
        "text": "st.text(min_size=0, max_size=100)",
        "lists": "st.lists(st.integers(), min_size=0, max_size=50)",
        "dictionaries": "st.dictionaries(st.text(), st.integers())",
        "dates": "st.dates(min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))",
        "custom_objects": "st.builds(YourClass, st.integers(), st.text())"
    }


def generate_property_testing_insights() -> List[str]:
    """Generate expert insights about property-based testing."""
    return [
        "Property-based testing finds edge cases you wouldn't think to test",
        "Start with simple properties and gradually add more complex ones",
        "Use shrinking to find minimal failing cases",
        "Combine property-based tests with example-based tests",
        "Focus on properties that capture the essence of your function",
        "Use stateful testing for classes and stateful systems",
        "Property tests are documentation - they describe what your code should do",
        "Don't test implementation details, test behavioral properties"
    ]
