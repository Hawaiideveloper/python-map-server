"""
Advanced sandboxing utilities for secure Python code execution.

This module provides enhanced security features beyond basic subprocess execution,
including resource limits, import restrictions, and security scanning.
"""

import os
import sys
import ast
import subprocess
import tempfile
import resource
import signal
import traceback
from typing import Dict, Any, List, Optional, Set
from pathlib import Path

# Dangerous imports that should be blocked
BLOCKED_IMPORTS = {
    # System access
    'subprocess', 'shutil', 'tempfile',
    'importlib', '__import__', 'eval', 'exec', 'compile',
    'input', 'raw_input', 'reload',
    
    # File system (controlled separately)
    'open', 'file',
    
    # Network (only specific safe ones allowed)
    'socket', 'ftplib', 'smtplib', 'telnetlib',
    
    # Serialization risks
    'marshal', 'shelve',
    
    # System control
    'ctypes', 'multiprocessing', 'threading', 'asyncio',
    
    # OS access (controlled)
    'os', 'sys', 'glob'
}

# Safe imports that are allowed
ALLOWED_IMPORTS = {
    # Built-in safe modules
    'math', 'random', 'datetime', 'time', 'json', 'csv',
    'collections', 'itertools', 'functools', 'operator',
    'string', 're', 'hashlib', 'base64', 'uuid', 'decimal',
    'fractions', 'statistics', 'calendar', 'copy', 'pickle',
    'enum', 'dataclasses', 'typing', 'abc', 'warnings',
    
    # Data science and analysis
    'numpy', 'np', 'pandas', 'pd', 'matplotlib', 'plt', 
    'seaborn', 'sns', 'scipy', 'plotly', 'sklearn', 'scikit-learn',
    'polars', 'pl', 'dask',
    
    # Machine Learning & AI
    'torch', 'torchvision', 'tensorflow', 'tf', 'keras',
    'transformers', 'tokenizers', 'sentence_transformers',
    'xgboost', 'xgb', 'lightgbm', 'lgb',
    
    # LLM & AI Libraries
    'openai', 'anthropic', 'langchain', 'langchain_community',
    'langchain_openai', 'langchain_anthropic', 'llama_index',
    'chromadb', 'faiss', 'pinecone',
    
    # NLP & Text Processing
    'spacy', 'nltk', 'textblob', 'gensim',
    
    # Computer Vision & Media
    'cv2', 'opencv', 'mediapipe', 'PIL', 'Pillow', 
    'imageio', 'skimage', 'librosa', 'pydub',
    
    # Vector Databases
    'weaviate', 'qdrant_client', 'qdrant',
    
    # MLOps & Tracking
    'mlflow', 'wandb',
    
    # Web and networking (controlled)
    'requests', 'httpx', 'urllib', 'http', 'html',
    'beautifulsoup4', 'bs4', 'lxml', 'selenium', 'scrapy',
    'aiohttp', 'asyncio',
    
    # Time Series & Statistics
    'prophet', 'statsmodels', 'networkx',
    
    # Financial & Geographic
    'yfinance', 'alpha_vantage', 'geopandas', 'folium',
    
    # Database connectors
    'psycopg2', 'pymongo', 'redis', 'sqlite3',
    
    # Cloud SDKs
    'boto3', 'botocore', 'google', 'azure',
    
    # Jupyter & Development
    'jupyter', 'IPython', 'ipykernel',
    
    # Utilities
    'dateutil', 'pytz', 'yaml', 'toml', 'configparser',
    'argparse', 'logging', 'pathlib', 'textwrap',
    'rich', 'click', 'typer', 'pydantic'
}

class SecurityViolation(Exception):
    """Raised when code violates security policies."""
    pass

class ResourceLimitExceeded(Exception):
    """Raised when code exceeds resource limits."""
    pass

class CodeSecurityAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze code for security violations."""
    
    def __init__(self):
        self.violations = []
        self.imports = set()
        self.function_calls = []
        
    def visit_Import(self, node):
        for alias in node.names:
            module = alias.name.split('.')[0]
            self.imports.add(module)
            if module in BLOCKED_IMPORTS:
                self.violations.append(f"Blocked import: {module}")
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        if node.module:
            module = node.module.split('.')[0]
            self.imports.add(module)
            if module in BLOCKED_IMPORTS:
                self.violations.append(f"Blocked import from: {module}")
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            self.function_calls.append(func_name)
            
            # Check for dangerous function calls
            dangerous_funcs = {'eval', 'exec', 'compile', '__import__'}
            if func_name in dangerous_funcs:
                self.violations.append(f"Dangerous function call: {func_name}")
                
        self.generic_visit(node)

def analyze_code_security(code: str) -> Dict[str, Any]:
    """
    Analyze Python code for security violations.
    
    Args:
        code: Python code to analyze
        
    Returns:
        Dict with security analysis results
    """
    try:
        tree = ast.parse(code)
        analyzer = CodeSecurityAnalyzer()
        analyzer.visit(tree)
        
        return {
            "is_safe": len(analyzer.violations) == 0,
            "violations": analyzer.violations,
            "imports": list(analyzer.imports),
            "function_calls": analyzer.function_calls,
            "allowed_imports": [imp for imp in analyzer.imports if imp in ALLOWED_IMPORTS],
            "blocked_imports": [imp for imp in analyzer.imports if imp in BLOCKED_IMPORTS]
        }
        
    except SyntaxError as e:
        return {
            "is_safe": False,
            "violations": [f"Syntax error: {str(e)}"],
            "imports": [],
            "function_calls": []
        }

def set_resource_limits():
    """Set resource limits for subprocess execution."""
    # Limit CPU time to 30 seconds
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    
    # Limit memory usage to 256MB
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
    
    # Limit number of processes
    resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
    
    # Limit file size to 10MB
    resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))

def create_restricted_environment() -> Dict[str, str]:
    """Create a restricted environment for code execution."""
    env = os.environ.copy()
    
    # Remove potentially dangerous environment variables
    dangerous_vars = [
        'PATH', 'PYTHONPATH', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH',
        'HOME', 'USER', 'USERNAME', 'LOGNAME'
    ]
    
    for var in dangerous_vars:
        env.pop(var, None)
    
    # Set minimal safe environment
    env.update({
        'PATH': '/usr/bin:/bin',
        'PYTHONDONTWRITEBYTECODE': '1',
        'PYTHONUNBUFFERED': '1',
        'PYTHONHASHSEED': '0'
    })
    
    return env

def execute_code_securely(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute Python code with enhanced security measures.
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        
    Returns:
        Dict with execution results and security info
    """
    # First, analyze code for security violations
    security_analysis = analyze_code_security(code)
    
    if not security_analysis["is_safe"]:
        return {
            "status": "error",
            "error": "Security violation detected",
            "security_violations": security_analysis["violations"],
            "blocked_imports": security_analysis["blocked_imports"]
        }
    
    try:
        # Create temporary file with restricted permissions
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.py', 
            delete=False,
            dir='/tmp'
        ) as tmp:
            tmp.write(code)
            tmp.flush()
            
            # Set restrictive file permissions
            os.chmod(tmp.name, 0o600)
            
            # Prepare restricted environment
            env = create_restricted_environment()
            
            # Execute with resource limits
            result = subprocess.run(
                [sys.executable, tmp.name],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                preexec_fn=set_resource_limits,  # Unix only
                cwd='/tmp'  # Restrict working directory
            )
            
            return {
                "status": "success",
                "result": {
                    "stdout": result.stdout[:5000],  # Limit output size
                    "stderr": result.stderr[:5000],
                    "returncode": result.returncode
                },
                "security_analysis": security_analysis,
                "execution_time": timeout
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": f"Code execution timed out after {timeout} seconds",
            "security_analysis": security_analysis
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Execution failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "security_analysis": security_analysis
        }
    finally:
        # Clean up temporary file
        try:
            if 'tmp' in locals():
                os.unlink(tmp.name)
        except OSError:
            pass  # Best effort cleanup

def validate_code_safety(code: str) -> Dict[str, Any]:
    """
    Validate code safety without executing it.
    
    Args:
        code: Python code to validate
        
    Returns:
        Dict with validation results
    """
    # Check code length
    if len(code) > 10000:
        return {
            "is_safe": False,
            "reason": "Code too long (>10000 characters)"
        }
    
    # Security analysis
    security_analysis = analyze_code_security(code)
    
    if not security_analysis["is_safe"]:
        return {
            "is_safe": False,
            "reason": "Security violations detected",
            "violations": security_analysis["violations"]
        }
    
    # Check for infinite loops (basic patterns)
    dangerous_patterns = [
        'while True:', 'while 1:', 'for i in itertools.count()',
        'while not False:', 'while 1 == 1:'
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            return {
                "is_safe": False,
                "reason": f"Potentially infinite loop detected: {pattern}"
            }
    
    return {
        "is_safe": True,
        "reason": "Code passed safety checks",
        "security_analysis": security_analysis
    }
