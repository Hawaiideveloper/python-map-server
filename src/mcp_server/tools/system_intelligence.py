"""
Advanced system intelligence and automation tools for the Python MCP Server.

This module provides intelligent automation, code analysis, system monitoring,
and advanced development assistance features.
"""

import os
import sys
import json
import traceback
import subprocess
import psutil
import time
import sqlite3
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from ..utils.logging import log_tool_execution
from ..utils.security import validate_code_safety
from ..config import TEMP_DIR, MAX_EXECUTION_TIME, DATABASE_URL

@log_tool_execution("system_info")
def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        Dict with system details, performance metrics, and environment info
    """
    try:
        # System information
        cpu_info = {
            "count": psutil.cpu_count(),
            "usage_percent": psutil.cpu_percent(interval=1),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        memory_info = psutil.virtual_memory()._asdict()
        disk_info = psutil.disk_usage('/')._asdict()
        
        # Python environment
        python_info = {
            "version": sys.version,
            "executable": sys.executable,
            "path": sys.path[:5],  # First 5 paths only
            "platform": sys.platform
        }
        
        # Installed packages
        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            packages = json.loads(result.stdout) if result.returncode == 0 else []
        except Exception:
            packages = []
        
        return {
            "status": "success",
            "result": {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "python": python_info,
                "packages": packages[:20],  # First 20 packages
                "environment_variables": dict(os.environ)
            },
            "metadata": {
                "tool": "system_info",
                "timestamp": time.time()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "system_info"
        }

@log_tool_execution("code_intelligence")
def analyze_code_intelligence(code: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """
    Perform intelligent code analysis with AI-powered insights.
    
    Args:
        code: Python code to analyze
        analysis_type: Type of analysis (complexity, security, performance, comprehensive)
        
    Returns:
        Dict with detailed code analysis results
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        # Security validation
        safety_check = validate_code_safety(code)
        if not safety_check["is_safe"]:
            raise ValueError(f"Code safety check failed: {safety_check['reason']}")
        
        import ast
        
        # Parse the code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "status": "error",
                "error": f"Syntax error: {e}",
                "tool": "code_intelligence"
            }
        
        analysis_results = {
            "syntax": "valid",
            "structure": analyze_ast_structure(tree),
            "complexity": calculate_complexity(tree),
            "imports": extract_imports(tree),
            "functions": extract_functions(tree),
            "classes": extract_classes(tree)
        }
        
        if analysis_type in ["security", "comprehensive"]:
            analysis_results["security"] = analyze_security_patterns(code, tree)
            
        if analysis_type in ["performance", "comprehensive"]:
            analysis_results["performance"] = analyze_performance_patterns(code, tree)
            
        # Code quality metrics
        lines = code.split('\n')
        analysis_results["metrics"] = {
            "lines_of_code": len([line for line in lines if line.strip()]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "docstring_coverage": calculate_docstring_coverage(tree)
        }
        
        return {
            "status": "success",
            "result": analysis_results,
            "metadata": {
                "tool": "code_intelligence",
                "analysis_type": analysis_type
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "code_intelligence"
        }

@log_tool_execution("smart_debug")
def smart_debug_assistance(code: str, error_message: str = "") -> Dict[str, Any]:
    """
    Provide intelligent debugging assistance with suggestions.
    
    Args:
        code: Python code that has issues
        error_message: Error message or traceback (optional)
        
    Returns:
        Dict with debugging suggestions and fixes
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        suggestions = []
        fixes = []
        
        # Common error patterns
        error_patterns = {
            "IndentationError": "Check for consistent indentation (tabs vs spaces)",
            "NameError": "Variable or function name not defined - check spelling and scope",
            "TypeError": "Type mismatch - check data types and function signatures",
            "AttributeError": "Object doesn't have the requested attribute - check object type",
            "ImportError": "Module not found - check installation and import path",
            "KeyError": "Dictionary key not found - use .get() or check key existence",
            "IndexError": "List index out of range - check list length before accessing",
            "SyntaxError": "Invalid Python syntax - check parentheses, quotes, and colons"
        }
        
        # Analyze error message
        if error_message:
            for error_type, suggestion in error_patterns.items():
                if error_type in error_message:
                    suggestions.append({
                        "type": "error_pattern",
                        "message": suggestion,
                        "confidence": 0.8
                    })
        
        # Code analysis for common issues
        lines = code.split('\n')
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Indentation issues
            if line.startswith(' ') and line.startswith('\t'):
                suggestions.append({
                    "type": "mixed_indentation",
                    "line": i,
                    "message": "Mixed spaces and tabs detected",
                    "confidence": 0.9
                })
            
            # Missing colons
            if any(keyword in stripped for keyword in ['if ', 'for ', 'while ', 'def ', 'class ']):
                if not stripped.endswith(':') and not stripped.endswith('\\'):
                    suggestions.append({
                        "type": "missing_colon",
                        "line": i,
                        "message": "Missing colon at end of statement",
                        "confidence": 0.7
                    })
            
            # Unmatched parentheses/brackets
            open_chars = '([{'
            close_chars = ')]}'
            stack = []
            for char in stripped:
                if char in open_chars:
                    stack.append(char)
                elif char in close_chars:
                    if not stack:
                        suggestions.append({
                            "type": "unmatched_bracket",
                            "line": i,
                            "message": f"Unmatched closing bracket: {char}",
                            "confidence": 0.8
                        })
                    else:
                        expected = close_chars[open_chars.index(stack.pop())]
                        if char != expected:
                            suggestions.append({
                                "type": "mismatched_bracket",
                                "line": i,
                                "message": f"Expected {expected}, got {char}",
                                "confidence": 0.8
                            })
        
        # Try to provide automatic fixes for simple issues
        if suggestions:
            fixes = generate_code_fixes(code, suggestions)
        
        return {
            "status": "success",
            "result": {
                "suggestions": suggestions,
                "fixes": fixes,
                "error_analysis": analyze_error_context(error_message) if error_message else None
            },
            "metadata": {
                "tool": "smart_debug",
                "suggestions_count": len(suggestions)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "smart_debug"
        }

@log_tool_execution("project_scaffold")
def create_project_scaffold(project_name: str, project_type: str = "basic", 
                          features: List[str] = None) -> Dict[str, Any]:
    """
    Create intelligent project scaffolding with best practices.
    
    Args:
        project_name: Name of the project
        project_type: Type of project (basic, web, ml, data_science, cli)
        features: List of features to include
        
    Returns:
        Dict with created project structure
    """
    try:
        if not project_name:
            raise ValueError("project_name is required")
            
        features = features or []
        project_path = Path(TEMP_DIR) / project_name
        
        # Create project directory
        project_path.mkdir(exist_ok=True)
        
        # Basic structure
        created_files = []
        
        # README.md
        readme_content = generate_readme(project_name, project_type, features)
        (project_path / "README.md").write_text(readme_content)
        created_files.append("README.md")
        
        # Project structure based on type
        if project_type == "web":
            structure = create_web_project_structure(project_path, features)
        elif project_type == "ml":
            structure = create_ml_project_structure(project_path, features)
        elif project_type == "data_science":
            structure = create_data_science_structure(project_path, features)
        elif project_type == "cli":
            structure = create_cli_project_structure(project_path, features)
        else:
            structure = create_basic_project_structure(project_path, features)
        
        created_files.extend(structure)
        
        # Generate requirements.txt based on project type
        requirements = generate_requirements(project_type, features)
        if requirements:
            (project_path / "requirements.txt").write_text('\n'.join(requirements))
            created_files.append("requirements.txt")
        
        return {
            "status": "success",
            "result": {
                "project_path": str(project_path),
                "project_type": project_type,
                "features": features,
                "created_files": created_files,
                "next_steps": generate_next_steps(project_type, features)
            },
            "metadata": {
                "tool": "project_scaffold",
                "files_created": len(created_files)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "project_scaffold"
        }

# Helper functions for code analysis
def analyze_ast_structure(tree) -> Dict[str, Any]:
    """Analyze AST structure for code insights."""
    import ast
    
    structure = {
        "imports": 0,
        "functions": 0,
        "classes": 0,
        "statements": 0,
        "max_nesting_level": 0
    }
    
    class StructureVisitor(ast.NodeVisitor):
        def __init__(self):
            self.nesting_level = 0
            self.max_nesting = 0
            
        def visit_Import(self, node):
            structure["imports"] += 1
            self.generic_visit(node)
            
        def visit_ImportFrom(self, node):
            structure["imports"] += 1
            self.generic_visit(node)
            
        def visit_FunctionDef(self, node):
            structure["functions"] += 1
            self.nesting_level += 1
            self.max_nesting = max(self.max_nesting, self.nesting_level)
            self.generic_visit(node)
            self.nesting_level -= 1
            
        def visit_ClassDef(self, node):
            structure["classes"] += 1
            self.nesting_level += 1
            self.max_nesting = max(self.max_nesting, self.nesting_level)
            self.generic_visit(node)
            self.nesting_level -= 1
    
    visitor = StructureVisitor()
    visitor.visit(tree)
    structure["max_nesting_level"] = visitor.max_nesting
    
    return structure

def calculate_complexity(tree) -> Dict[str, Any]:
    """Calculate cyclomatic complexity."""
    import ast
    
    complexity = {"total": 1, "functions": {}}
    
    class ComplexityVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_function = None
            
        def visit_FunctionDef(self, node):
            self.current_function = node.name
            complexity["functions"][node.name] = 1
            self.generic_visit(node)
            self.current_function = None
            
        def visit_If(self, node):
            complexity["total"] += 1
            if self.current_function:
                complexity["functions"][self.current_function] += 1
            self.generic_visit(node)
            
        def visit_For(self, node):
            complexity["total"] += 1
            if self.current_function:
                complexity["functions"][self.current_function] += 1
            self.generic_visit(node)
            
        def visit_While(self, node):
            complexity["total"] += 1
            if self.current_function:
                complexity["functions"][self.current_function] += 1
            self.generic_visit(node)
    
    visitor = ComplexityVisitor()
    visitor.visit(tree)
    
    return complexity

def extract_imports(tree) -> List[str]:
    """Extract all imports from the AST."""
    import ast
    
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for name in node.names:
                imports.append(f"{module}.{name.name}" if module else name.name)
    
    return imports

def extract_functions(tree) -> List[Dict[str, Any]]:
    """Extract function definitions and their details."""
    import ast
    
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = {
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "lineno": node.lineno,
                "has_docstring": ast.get_docstring(node) is not None
            }
            functions.append(func_info)
    
    return functions

def extract_classes(tree) -> List[Dict[str, Any]]:
    """Extract class definitions and their details."""
    import ast
    
    classes = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                "lineno": node.lineno,
                "has_docstring": ast.get_docstring(node) is not None,
                "methods": []
            }
            
            # Extract methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_info["methods"].append(item.name)
            
            classes.append(class_info)
    
    return classes

def analyze_security_patterns(code: str, tree) -> Dict[str, Any]:
    """Analyze code for security patterns and issues."""
    import ast
    
    security_issues = []
    
    # Check for dangerous patterns
    dangerous_patterns = [
        "eval(", "exec(", "compile(", "__import__(",
        "subprocess.call", "os.system", "input(",
        "pickle.loads", "marshal.loads"
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            security_issues.append({
                "type": "dangerous_function",
                "pattern": pattern,
                "severity": "high"
            })
    
    return {
        "issues": security_issues,
        "risk_level": "high" if security_issues else "low"
    }

def analyze_performance_patterns(code: str, tree) -> Dict[str, Any]:
    """Analyze code for performance patterns and suggestions."""
    performance_suggestions = []
    
    # Check for common performance issues
    if "for i in range(len(" in code:
        performance_suggestions.append({
            "type": "loop_optimization",
            "message": "Consider using enumerate() instead of range(len())",
            "severity": "medium"
        })
    
    if ".append(" in code and "for " in code:
        performance_suggestions.append({
            "type": "list_comprehension",
            "message": "Consider using list comprehension for better performance",
            "severity": "low"
        })
    
    return {
        "suggestions": performance_suggestions,
        "optimization_score": max(0, 100 - len(performance_suggestions) * 10)
    }

def calculate_docstring_coverage(tree) -> float:
    """Calculate the percentage of functions/classes with docstrings."""
    import ast
    
    total_items = 0
    documented_items = 0
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            total_items += 1
            if ast.get_docstring(node):
                documented_items += 1
    
    return (documented_items / total_items * 100) if total_items > 0 else 100

def generate_code_fixes(code: str, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate automatic fixes for common code issues."""
    fixes = []
    
    for suggestion in suggestions:
        if suggestion["type"] == "missing_colon":
            line_num = suggestion["line"]
            lines = code.split('\n')
            if line_num <= len(lines):
                fixed_line = lines[line_num - 1] + ":"
                fixes.append({
                    "type": "missing_colon",
                    "line": line_num,
                    "original": lines[line_num - 1],
                    "fixed": fixed_line,
                    "confidence": 0.9
                })
    
    return fixes

def analyze_error_context(error_message: str) -> Dict[str, Any]:
    """Analyze error message for additional context."""
    context = {
        "error_type": "unknown",
        "line_number": None,
        "column": None,
        "suggestions": []
    }
    
    # Extract error type
    if ":" in error_message:
        context["error_type"] = error_message.split(":")[0].strip()
    
    # Extract line information
    import re
    line_match = re.search(r'line (\d+)', error_message)
    if line_match:
        context["line_number"] = int(line_match.group(1))
    
    return context

# Project scaffolding helper functions
def generate_readme(project_name: str, project_type: str, features: List[str]) -> str:
    """Generate README.md content."""
    content = f"""# {project_name}

A {project_type} project created with MCP Server scaffolding.

## Features

"""
    
    if features:
        for feature in features:
            content += f"- {feature}\n"
    else:
        content += "- Basic project structure\n"
    
    content += """
## Installation

```bash
pip install -r requirements.txt
```

## Usage

TODO: Add usage instructions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
"""
    
    return content

def create_basic_project_structure(project_path: Path, features: List[str]) -> List[str]:
    """Create basic project structure."""
    files = []
    
    # Create main module
    (project_path / "main.py").write_text('"""Main module."""\n\nif __name__ == "__main__":\n    print("Hello, World!")\n')
    files.append("main.py")
    
    # Create tests directory
    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_main.py").write_text('"""Test main module."""\n\ndef test_example():\n    assert True\n')
    files.extend(["tests/__init__.py", "tests/test_main.py"])
    
    return files

def create_web_project_structure(project_path: Path, features: List[str]) -> List[str]:
    """Create web project structure."""
    files = []
    
    # Create app structure
    app_dir = project_path / "app"
    app_dir.mkdir(exist_ok=True)
    
    (app_dir / "__init__.py").write_text("")
    (app_dir / "main.py").write_text('''"""Web application main module."""

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')
    
    files.extend(["app/__init__.py", "app/main.py"])
    
    return files

def create_ml_project_structure(project_path: Path, features: List[str]) -> List[str]:
    """Create machine learning project structure."""
    files = []
    
    # Create ML directories
    for dir_name in ["data", "models", "notebooks", "src"]:
        (project_path / dir_name).mkdir(exist_ok=True)
        (project_path / dir_name / ".gitkeep").write_text("")
        files.append(f"{dir_name}/.gitkeep")
    
    # Create main training script
    (project_path / "train.py").write_text('''"""Model training script."""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_model():
    # Load data
    # data = pd.read_csv("data/dataset.csv")
    
    # Train model
    # model = RandomForestClassifier()
    # model.fit(X_train, y_train)
    
    # Save model
    # joblib.dump(model, "models/model.pkl")
    
    print("Model training completed")

if __name__ == "__main__":
    train_model()
''')
    files.append("train.py")
    
    return files

def create_data_science_structure(project_path: Path, features: List[str]) -> List[str]:
    """Create data science project structure."""
    files = []
    
    # Create data science directories
    for dir_name in ["data/raw", "data/processed", "notebooks", "reports", "src"]:
        (project_path / dir_name).mkdir(parents=True, exist_ok=True)
        (project_path / dir_name / ".gitkeep").write_text("")
        files.append(f"{dir_name}/.gitkeep")
    
    # Create example notebook
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Data Analysis Notebook"]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["import pandas as pd", "import numpy as np", "import matplotlib.pyplot as plt"]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    import json
    (project_path / "notebooks" / "analysis.ipynb").write_text(json.dumps(notebook_content, indent=2))
    files.append("notebooks/analysis.ipynb")
    
    return files

def create_cli_project_structure(project_path: Path, features: List[str]) -> List[str]:
    """Create CLI project structure."""
    files = []
    
    # Create CLI module
    (project_path / "cli.py").write_text('''"""Command line interface."""

import argparse

def main():
    parser = argparse.ArgumentParser(description="CLI application")
    parser.add_argument("--version", action="version", version="1.0.0")
    parser.add_argument("command", help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "hello":
        print("Hello, World!")
    else:
        print(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
''')
    files.append("cli.py")
    
    return files

def generate_requirements(project_type: str, features: List[str]) -> List[str]:
    """Generate requirements based on project type."""
    base_requirements = ["pytest>=7.0.0"]
    
    if project_type == "web":
        base_requirements.extend(["fastapi>=0.95.0", "uvicorn>=0.22.0"])
    elif project_type == "ml":
        base_requirements.extend([
            "scikit-learn>=1.3.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "joblib>=1.3.0"
        ])
    elif project_type == "data_science":
        base_requirements.extend([
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "jupyter>=1.0.0"
        ])
    
    return base_requirements

def generate_next_steps(project_type: str, features: List[str]) -> List[str]:
    """Generate next steps for the project."""
    steps = [
        "Install dependencies: pip install -r requirements.txt",
        "Initialize git repository: git init",
        "Create virtual environment: python -m venv venv"
    ]
    
    if project_type == "web":
        steps.append("Run the web server: python app/main.py")
    elif project_type == "ml":
        steps.append("Add your dataset to the data/ directory")
        steps.append("Run training: python train.py")
    elif project_type == "data_science":
        steps.append("Start Jupyter: jupyter lab")
        steps.append("Open notebooks/analysis.ipynb")
    
    return steps
