"""
Configuration and constants for the Python MCP Server.

This module centralizes all configuration values, constants, and settings
to help GitHub Copilot understand the project's configuration patterns.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DOCS_DIR = PROJECT_ROOT / "docs"
TESTS_DIR = PROJECT_ROOT / "tests"

# Execution settings
DEFAULT_TIMEOUT = 30  # seconds
MAX_CODE_LENGTH = 10000  # characters
MAX_OUTPUT_LENGTH = 5000  # characters

# Tool names (for MCP registration)
class ToolNames:
    RUN_CODE = "run_python"
    LINT_CODE = "lint_python" 
    FORMAT_CODE = "format_python"
    TEST_CODE = "test_python"
    GENERATE_DOCS = "generate_docs"
    AWS_S3_UPLOAD = "aws_upload_s3"
    GCP_LIST_BUCKET = "gcp_list_bucket"
    AZURE_DOWNLOAD_BLOB = "azure_download_blob"

# HTTP endpoints
class Endpoints:
    RUN_CODE = "/run_code"
    LINT_CODE = "/lint_code"
    FORMAT_CODE = "/format_code"
    TEST_CODE = "/test_code"
    GENERATE_DOCS = "/generate_docs"
    AWS_OPERATIONS = "/aws"
    GCP_OPERATIONS = "/gcp"
    AZURE_OPERATIONS = "/azure"

# Environment variables
class EnvVars:
    # AWS
    AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
    AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
    AWS_REGION = "AWS_REGION"
    
    # GCP
    GCP_PROJECT = "GCP_PROJECT"
    GCP_CREDENTIALS_PATH = "GCP_CREDENTIALS_PATH"
    
    # Azure
    AZURE_STORAGE_CONNECTION_STRING = "AZURE_STORAGE_CONNECTION_STRING"
    
    # Server
    HOST = "HOST"
    PORT = "PORT"
    DEBUG = "DEBUG"

# Default values
DEFAULTS = {
    "host": "0.0.0.0",
    "port": 8080,
    "debug": False,
    "aws_region": "us-east-1",
}

# Tool configurations
TOOL_CONFIGS = {
    "ruff": {
        "command": ["ruff", "check"],
        "format_command": ["ruff", "format"],
        "config_files": ["pyproject.toml", "ruff.toml", ".ruff.toml"]
    },
    "black": {
        "command": ["black"],
        "line_length": 88,
        "config_files": ["pyproject.toml", "black.toml"]
    },
    "pytest": {
        "command": ["pytest"],
        "config_files": ["pytest.ini", "pyproject.toml", "setup.cfg"]
    },
    "bandit": {
        "command": ["bandit", "-r"],
        "config_files": [".bandit", "pyproject.toml"]
    }
}

# Security settings
SECURITY_SETTINGS = {
    "max_execution_time": DEFAULT_TIMEOUT,
    "allowed_imports": [
        "os", "sys", "json", "math", "random", "datetime", "time",
        "collections", "itertools", "functools", "operator",
        "requests", "numpy", "pandas", "matplotlib", "seaborn"
    ],
    "blocked_imports": [
        "subprocess", "eval", "exec", "compile", "open",
        "input", "raw_input", "__import__"
    ]
}

def get_env_var(name: str, default: Any = None) -> str:
    """Get environment variable with fallback to default."""
    return os.getenv(name, default)

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary."""
    return {
        "host": get_env_var(EnvVars.HOST, DEFAULTS["host"]),
        "port": int(get_env_var(EnvVars.PORT, DEFAULTS["port"])),
        "debug": get_env_var(EnvVars.DEBUG, DEFAULTS["debug"]) == "true",
        "aws": {
            "access_key_id": get_env_var(EnvVars.AWS_ACCESS_KEY_ID),
            "secret_access_key": get_env_var(EnvVars.AWS_SECRET_ACCESS_KEY),
            "region": get_env_var(EnvVars.AWS_REGION, DEFAULTS["aws_region"]),
        },
        "gcp": {
            "project": get_env_var(EnvVars.GCP_PROJECT),
            "credentials_path": get_env_var(EnvVars.GCP_CREDENTIALS_PATH),
        },
        "azure": {
            "connection_string": get_env_var(EnvVars.AZURE_STORAGE_CONNECTION_STRING),
        }
    }
