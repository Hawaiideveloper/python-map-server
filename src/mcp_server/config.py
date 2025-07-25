"""
Configuration module for the Python MCP Server.

This module handles all configuration settings, environment variables,
and provides default values for the server and tools.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent.parent.absolute()
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
TEMP_DIR = BASE_DIR / "temp"

# Create directories if they don't exist
for dir_path in [DATA_DIR, LOGS_DIR, MODELS_DIR, TEMP_DIR]:
    dir_path.mkdir(exist_ok=True)

# Server Configuration
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8080"))
MCP_DEBUG = os.getenv("MCP_DEBUG", "false").lower() == "true"
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "true").lower() == "true"
AUTO_RELOAD = os.getenv("AUTO_RELOAD", "true").lower() == "true"

# API Keys and Authentication
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
WANDB_API_KEY = os.getenv("WANDB_API_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-change-in-production")

# Rate Limiting
API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "100"))
API_RATE_LIMIT_WINDOW = int(os.getenv("API_RATE_LIMIT_WINDOW", "3600"))

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/mcp_server.db")

# Cloud Provider Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
GCP_PROJECT = os.getenv("GCP_PROJECT")
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", str(BASE_DIR / "chroma_db"))
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")

# MLflow Configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "mcp_server.log"))

# Jupyter Configuration
JUPYTER_PORT = int(os.getenv("JUPYTER_PORT", "8888"))
JUPYTER_TOKEN = os.getenv("JUPYTER_TOKEN")

# Security Configuration
BLOCKED_COMMANDS = [
    "rm", "rmdir", "del", "format", "fdisk",
    "mount", "umount", "sudo", "su", "passwd",
    "chmod", "chown", "kill", "killall"
]

# Code execution limits
MAX_EXECUTION_TIME = 30  # seconds
MAX_OUTPUT_SIZE = 5000  # characters
MAX_MEMORY_MB = 512  # MB

# Default model configurations
DEFAULT_MODELS = {
    "openai": {
        "chat": "gpt-3.5-turbo",
        "embeddings": "text-embedding-ada-002",
        "max_tokens": 1000
    },
    "anthropic": {
        "chat": "claude-3-sonnet-20240229",
        "max_tokens": 1000
    },
    "sklearn": {
        "classification": "random_forest",
        "regression": "random_forest",
        "clustering": "kmeans"
    }
}

# Tool-specific configurations
TOOL_CONFIGS = {
    "run_code": {
        "timeout": MAX_EXECUTION_TIME,
        "max_output": MAX_OUTPUT_SIZE,
        "temp_dir": str(TEMP_DIR)
    },
    "lint_code": {
        "timeout": 10,
        "rules": ["E", "F", "W", "I", "N"]
    },
    "format_code": {
        "line_length": 88,
        "timeout": 10
    },
    "test_code": {
        "timeout": 60,
        "coverage": True
    },
    "ai_chat": {
        "timeout": 30,
        "retry_attempts": 3
    },
    "embeddings": {
        "batch_size": 100,
        "timeout": 60
    },
    "vector_search": {
        "default_top_k": 5,
        "max_top_k": 50
    }
}

def get_config(key: str, default: Any = None) -> Any:
    """
    Get configuration value by key.
    
    Args:
        key: Configuration key (dot notation supported)
        default: Default value if key not found
        
    Returns:
        Configuration value
    """
    if "." in key:
        # Handle nested keys like "tool_configs.run_code.timeout"
        keys = key.split(".")
        value = globals()
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    return globals().get(key.upper(), default)

def validate_required_keys() -> Dict[str, bool]:
    """
    Validate that required configuration keys are set.
    
    Returns:
        Dict with validation results
    """
    validations = {
        "openai_api_key": bool(OPENAI_API_KEY),
        "jwt_secret_key": JWT_SECRET_KEY != "fallback-secret-key-change-in-production",
        "database_configured": bool(DATABASE_URL)
    }
    
    return validations

def get_database_config() -> Dict[str, str]:
    """Get database configuration details."""
    return {
        "url": DATABASE_URL,
        "driver": DATABASE_URL.split("://")[0] if "://" in DATABASE_URL else "sqlite"
    }

def get_cloud_config() -> Dict[str, Dict[str, Optional[str]]]:
    """Get cloud provider configurations."""
    return {
        "aws": {
            "access_key_id": AWS_ACCESS_KEY_ID,
            "secret_access_key": AWS_SECRET_ACCESS_KEY,
            "region": AWS_REGION
        },
        "gcp": {
            "project": GCP_PROJECT,
            "credentials_path": GCP_CREDENTIALS_PATH
        },
        "azure": {
            "connection_string": AZURE_STORAGE_CONNECTION_STRING
        }
    }

def get_vector_db_config() -> Dict[str, str]:
    """Get vector database configurations."""
    return {
        "chroma": {
            "persist_directory": CHROMA_PERSIST_DIRECTORY
        },
        "qdrant": {
            "url": QDRANT_URL
        },
        "weaviate": {
            "url": WEAVIATE_URL
        }
    }

# Legacy compatibility - keep existing constants for backward compatibility  
MAX_OUTPUT_LENGTH = MAX_OUTPUT_SIZE
DEFAULT_TIMEOUT = MAX_EXECUTION_TIME
PROJECT_ROOT = BASE_DIR
SRC_DIR = BASE_DIR / "src"
DOCS_DIR = BASE_DIR / "docs"
TESTS_DIR = BASE_DIR / "tests"
MAX_CODE_LENGTH = 10000

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
    AI_CHAT = "ai_chat"
    CREATE_EMBEDDINGS = "create_embeddings"
    VECTOR_SEARCH = "vector_search"
    TRAIN_ML_MODEL = "train_ml_model"
    ANALYZE_TEXT = "analyze_text"
    ANALYZE_IMAGE = "analyze_image"

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
    AI_CHAT = "/ai/chat"
    AI_EMBEDDINGS = "/ai/embeddings"
    AI_VECTOR_SEARCH = "/ai/vector_search"
    AI_TRAIN_MODEL = "/ai/train_model"
    AI_ANALYZE_TEXT = "/ai/analyze_text"
    AI_ANALYZE_IMAGE = "/ai/analyze_image"

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
    
    # AI/LLM
    OPENAI_API_KEY = "OPENAI_API_KEY"
    ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"
    PINECONE_API_KEY = "PINECONE_API_KEY"
    WANDB_API_KEY = "WANDB_API_KEY"

# Default configurations for tools
DEFAULTS = {
    "run_code": {
        "timeout": DEFAULT_TIMEOUT,
        "max_output_length": MAX_OUTPUT_LENGTH,
        "working_directory": str(BASE_DIR / "temp")
    },
    "lint_code": {
        "timeout": 10,
        "max_line_length": 88
    },
    "format_code": {
        "timeout": 10,
        "line_length": 88
    },
    "test_code": {
        "timeout": 60,
        "coverage": True
    },
    "ai_models": DEFAULT_MODELS
}

# Export commonly used configurations
__all__ = [
    "BASE_DIR", "DATA_DIR", "LOGS_DIR", "MODELS_DIR", "TEMP_DIR",
    "HTTP_HOST", "HTTP_PORT", "MCP_DEBUG", "DEVELOPMENT_MODE",
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "JWT_SECRET_KEY",
    "DATABASE_URL", "LOG_LEVEL", "LOG_FILE",
    "MAX_EXECUTION_TIME", "MAX_OUTPUT_SIZE", "MAX_MEMORY_MB",
    "DEFAULT_MODELS", "TOOL_CONFIGS", "DEFAULTS",
    "ToolNames", "Endpoints", "EnvVars",
    "get_config", "validate_required_keys", "get_database_config",
    "get_cloud_config", "get_vector_db_config"
]
