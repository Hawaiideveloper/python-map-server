
"""
Enhanced Python MCP Server with AI/LLM integration and comprehensive tooling.

This module implements the main MCP server with JSON-RPC protocol support,
HTTP REST API bridge, security features, and comprehensive tool registration.
"""

import asyncio
import os
import sys
import threading
import time
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server.fastmcp.server import FastMCP

from mcp_server.config import DEVELOPMENT_MODE
from mcp_server.tools import (
    advanced_code_analysis,
    advanced_data_processing,
    advanced_testing,
    ai_tools,
    data_formats,
    doc_gen,
    documentation_manager,
    expert_patterns,
    format_code,
    lint_code,
    performance_profiling,
    run_code,
    sdk_integrations,
    smart_refactoring,
    system_intelligence,
    test_code,
    vcs_integration,
)
from mcp_server.utils.auth import authenticate_request, check_rate_limit
from mcp_server.utils.logging import log_http_request, setup_logger
from mcp_server.websocket_server import get_websocket_handler

# Setup logging
logger = setup_logger("mcp_server")

# Initialize FastMCP Server
mcp_server = FastMCP("python-mcp-server")

# Initialize FastAPI app for HTTP bridge
http_app = FastAPI(
    title="Python MCP Server HTTP Bridge",
    description="Comprehensive Python development platform with AI/LLM integration",
    version="0.3.0",
    docs_url="/docs" if DEVELOPMENT_MODE else None,
    redoc_url="/redoc" if DEVELOPMENT_MODE else None
)

# Add CORS middleware
http_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEVELOPMENT_MODE else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check and info endpoints for Railway deployment
@http_app.get("/health")
@log_http_request("health_check")
async def health_check(request: Request):
    """Health check endpoint for Railway deployment monitoring"""
    return {
        "status": "healthy",
        "service": "python-mcp-server",
        "timestamp": time.time(),
        "version": "0.3.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "port": os.getenv("PORT", "8000")
    }

@http_app.get("/")
@log_http_request("root")
async def root(request: Request):
    """Root endpoint with service information"""
    # Get the actual host from the request
    host = request.headers.get("host", "localhost:8080")
    scheme = "https" if request.headers.get("x-forwarded-proto") == "https" else "http"
    ws_scheme = "wss" if scheme == "https" else "ws"
    
    return {
        "service": "Python MCP Server",
        "status": "running",
        "version": "0.3.0",
        "endpoints": {
            "health": "/health",
            "mcp_websocket": "/mcp",
            "run_code": "/run_code",
            "lint_code": "/lint_code",
            "format_code": "/format_code",
            "test_code": "/test_code",
            "ai_tools": "/ai/*",
            "system_tools": "/system/*",
            "sdk_tools": "/sdk/*"
        },
        "protocols": {
            "mcp_websocket": f"{ws_scheme}://{host}/mcp",
            "http_rest": f"{scheme}://{host}/"
        },
        "documentation": "/docs" if DEVELOPMENT_MODE else "Contact admin for API documentation"
    }

# WebSocket MCP Server Endpoint
@http_app.websocket("/mcp")
async def mcp_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for true MCP JSON-RPC protocol."""
    handler = get_websocket_handler(mcp_server)
    
    try:
        await handler.connect(websocket)
        logger.info("MCP WebSocket client connected")
        
        while True:
            # Receive MCP message
            message = await websocket.receive_text()
            
            # Process MCP request
            await handler.handle_mcp_message(websocket, message)
            
    except WebSocketDisconnect:
        logger.info("MCP WebSocket client disconnected")
        handler.disconnect(websocket)
    except Exception as e:
        logger.error(f"MCP WebSocket error: {e}")
        handler.disconnect(websocket)

# Register MCP Tools using FastMCP decorators

@mcp_server.tool(description="Execute Python code securely")
def run_python_tool(code: str) -> dict[str, Any]:
    """Execute Python code and return the result."""
    return run_code.run_python(code)

@mcp_server.tool(description="Lint Python code for syntax and style issues")
def lint_python_tool(code: str) -> dict[str, Any]:
    """Lint Python code and return issues found."""
    return lint_code.lint_python(code)

@mcp_server.tool(description="Format Python code using black")
def format_python_tool(code: str) -> dict[str, Any]:
    """Format Python code and return the formatted result."""
    return format_code.format_python(code)

@mcp_server.tool(description="Run tests on Python code")
def test_python_tool(code: str) -> dict[str, Any]:
    """Run tests on Python code and return results."""
    return test_code.test_python(code)

@mcp_server.tool(description="Generate documentation for Python code")
def generate_docs_tool(code: str) -> dict[str, Any]:
    """Generate documentation for Python code."""
    return doc_gen.generate_docs(code)

# AI/LLM Tools
@mcp_server.tool(description="Chat with AI models")
def ai_chat_tool(prompt: str, model: str = "gpt-3.5-turbo", provider: str = "openai") -> dict[str, Any]:
    """Chat with AI models and get responses."""
    return ai_tools.ai_chat(prompt, model, provider)

@mcp_server.tool(description="Create embeddings from text")
def create_embeddings_tool(texts: list[str], model: str = "text-embedding-ada-002") -> dict[str, Any]:
    """Create embeddings from text."""
    return ai_tools.create_embeddings(texts, model)

@mcp_server.tool(description="Search vector database")
def vector_search_tool(query: str, collection: str = "default", top_k: int = 5, vector_db: str = "chromadb") -> dict[str, Any]:
    """Search vector database for relevant results."""
    return ai_tools.vector_search(query, collection, top_k, vector_db)

@mcp_server.tool(description="Train machine learning model")
def train_ml_model_tool(data_code: str, model_type: str = "sklearn", algorithm: str = "random_forest") -> dict[str, Any]:
    """Train a machine learning model."""
    return ai_tools.train_ml_model(data_code, model_type, algorithm)

@mcp_server.tool(description="Analyze text using NLP")
def analyze_text_tool(text: str, analysis_type: str = "sentiment") -> dict[str, Any]:
    """Analyze text using natural language processing."""
    return ai_tools.analyze_text(text, analysis_type)

@mcp_server.tool(description="Analyze images using computer vision")
def analyze_image_tool(image_path: str, analysis_type: str = "objects") -> dict[str, Any]:
    """Analyze images using computer vision."""
    return ai_tools.analyze_image(image_path, analysis_type)

# System Intelligence Tools
@mcp_server.tool(description="Get system information")
def get_system_info_tool() -> dict[str, Any]:
    """Get comprehensive system information."""
    return system_intelligence.get_system_info()

@mcp_server.tool(description="Analyze code for intelligence insights")
def analyze_code_intelligence_tool(code: str, analysis_type: str = "comprehensive") -> dict[str, Any]:
    """Analyze code and provide intelligence insights."""
    return system_intelligence.analyze_code_intelligence(code, analysis_type)

@mcp_server.tool(description="Get smart debugging assistance")
def smart_debug_assistance_tool(code: str, error_message: str = "") -> dict[str, Any]:
    """Get smart debugging assistance for code issues."""
    return system_intelligence.smart_debug_assistance(code, error_message)

@mcp_server.tool(description="Create project scaffold")
def create_project_scaffold_tool(project_name: str, project_type: str = "basic", features: list[str] | None = None) -> dict[str, Any]:
    """Create a project scaffold with specified features."""
    if features is None:
        features = []
    return system_intelligence.create_project_scaffold(project_name, project_type, features)

# Cloud SDK Tools
@mcp_server.tool(description="Upload file to AWS S3")
def aws_upload_s3_tool(bucket: str, key: str, file_path: str) -> dict[str, Any]:
    """Upload a file to AWS S3."""
    return sdk_integrations.aws_upload_s3(bucket, key, file_path)

@mcp_server.tool(description="List objects in GCP bucket")
def gcp_list_bucket_tool(bucket: str) -> dict[str, Any]:
    """List objects in a Google Cloud Platform bucket."""
    return sdk_integrations.gcp_list_bucket(bucket)

@mcp_server.tool(description="Download blob from Azure storage")
def azure_download_blob_tool(container: str, blob_name: str, download_path: str) -> dict[str, Any]:
    """Download a blob from Azure storage."""
    return sdk_integrations.azure_download_blob(container, blob_name, download_path)

# Advanced Code Analysis Tools
@mcp_server.tool(description="Perform advanced type checking with mypy")
def type_check_tool(code: str, python_version: str = "3.12") -> dict[str, Any]:
    """Perform type checking using mypy with modern Python features."""
    return advanced_code_analysis.type_check_code(code, python_version)

@mcp_server.tool(description="Security analysis with bandit")
def security_scan_tool(code: str, confidence_level: str = "medium") -> dict[str, Any]:
    """Perform security analysis using bandit."""
    return advanced_code_analysis.security_scan(code, confidence_level)

@mcp_server.tool(description="Audit dependencies for vulnerabilities")
def dependency_audit_tool(requirements_content: str = "") -> dict[str, Any]:
    """Audit dependencies for security vulnerabilities using safety."""
    return advanced_code_analysis.audit_dependencies(requirements_content)

@mcp_server.tool(description="Intelligent code completion with Jedi")
def code_completion_tool(code: str, cursor_position: int = -1) -> dict[str, Any]:
    """Provide intelligent code completion using Jedi."""
    return advanced_code_analysis.intelligent_code_completion(code, cursor_position)

@mcp_server.tool(description="Analyze modern Python features")
def modern_python_analysis_tool(code: str) -> dict[str, Any]:
    """Analyze code for modern Python features and suggest improvements."""
    return advanced_code_analysis.analyze_modern_python_features(code)

# Smart Refactoring Tools
@mcp_server.tool(description="Smart code refactoring")
def smart_refactor_tool(code: str, refactor_type: str = "all") -> dict[str, Any]:
    """Perform intelligent code refactoring with multiple improvement strategies."""
    return smart_refactoring.smart_refactor(code, refactor_type)

@mcp_server.tool(description="Detect code smells and anti-patterns")
def detect_code_smells_tool(code: str) -> dict[str, Any]:
    """Detect code smells and anti-patterns in Python code."""
    return smart_refactoring.detect_code_smells(code)

@mcp_server.tool(description="Check backward compatibility")
def backward_compatibility_tool(code: str, target_version: str = "3.8") -> dict[str, Any]:
    """Check backward compatibility and suggest migration strategies."""
    return smart_refactoring.check_backward_compatibility(code, target_version)

# Performance Profiling Tools
@mcp_server.tool(description="Profile code performance")
def profile_performance_tool(code: str, sort_by: str = "cumulative") -> dict[str, Any]:
    """Profile Python code performance using cProfile."""
    return performance_profiling.profile_code_performance(code, sort_by)

@mcp_server.tool(description="Profile memory usage")
def memory_profile_tool(code: str) -> dict[str, Any]:
    """Profile memory usage of Python code."""
    return performance_profiling.profile_memory_usage(code)

@mcp_server.tool(description="Benchmark code variants")
def benchmark_code_tool(code_variants: list[str], iterations: int = 1000) -> dict[str, Any]:
    """Benchmark multiple code variants to find the fastest implementation."""
    return performance_profiling.benchmark_code_variants(code_variants, iterations)

@mcp_server.tool(description="Suggest performance optimizations")
def performance_optimize_tool(code: str) -> dict[str, Any]:
    """Analyze code and suggest performance optimizations."""
    return performance_profiling.suggest_performance_optimizations(code)

# Documentation Management Tools
@mcp_server.tool(description="Download Python documentation")
def download_docs_tool(versions: list[str] | None = None, format_type: str = "html", docs_dir: str = "docs/python_manuals") -> dict[str, Any]:
    """Download Python documentation for specified versions."""
    return documentation_manager.download_python_documentation(versions, format_type, docs_dir)

@mcp_server.tool(description="Search Python documentation")
def search_docs_tool(query: str, versions: list[str] | None = None, docs_dir: str = "docs/python_manuals") -> dict[str, Any]:
    """Search through downloaded Python documentation."""
    return documentation_manager.search_python_documentation(query, versions, docs_dir)

@mcp_server.tool(description="Get Python version features")
def version_features_tool(version: str) -> dict[str, Any]:
    """Get detailed features and changes for a specific Python version."""
    return documentation_manager.get_python_version_features(version)

@mcp_server.tool(description="Compare Python versions")
def compare_versions_tool(version1: str, version2: str) -> dict[str, Any]:
    """Compare features and changes between two Python versions."""
    return documentation_manager.compare_python_versions(version1, version2)

# Expert Pattern Tools
@mcp_server.tool(description="Analyze code architecture with expert insights")
def analyze_architecture_tool(code: str, project_type: str = "general") -> dict[str, Any]:
    """Analyze code architecture with expert-level insights."""
    return expert_patterns.analyze_code_architecture(code, project_type)

@mcp_server.tool(description="Generate expert code templates")
def generate_expert_templates_tool(pattern_type: str, use_case: str) -> dict[str, Any]:
    """Generate expert-level code templates and patterns."""
    return expert_patterns.generate_expert_code_templates(pattern_type, use_case)

@mcp_server.tool(description="Analyze async patterns")
def analyze_async_tool(code: str) -> dict[str, Any]:
    """Analyze asynchronous programming patterns and suggest improvements."""
    return expert_patterns.analyze_async_patterns(code)

@mcp_server.tool(description="Analyze enterprise patterns")
def analyze_enterprise_tool(code: str, codebase_context: str = "") -> dict[str, Any]:
    """Analyze enterprise-level patterns and practices."""
    return expert_patterns.analyze_enterprise_patterns(code, codebase_context)

# Advanced Testing Tools
@mcp_server.tool(description="Generate comprehensive test suite")
def generate_tests_tool(code: str, test_framework: str = "pytest") -> dict[str, Any]:
    """Generate comprehensive test suite for given code."""
    return advanced_testing.generate_comprehensive_tests(code, test_framework)

@mcp_server.tool(description="Analyze debugging opportunities")
def debug_analysis_tool(code: str, error_context: str = "") -> dict[str, Any]:
    """Analyze code for debugging opportunities and suggest strategies."""
    return advanced_testing.analyze_debugging_opportunities(code, error_context)

@mcp_server.tool(description="Analyze test quality")
def test_quality_tool(test_code: str) -> dict[str, Any]:
    """Analyze quality of existing test code."""
    return advanced_testing.analyze_test_quality(test_code)

@mcp_server.tool(description="Suggest mutation testing")
def mutation_testing_tool(code: str, test_code: str) -> dict[str, Any]:
    """Suggest mutation testing strategies to improve test quality."""
    return advanced_testing.suggest_mutation_testing(code, test_code)

@mcp_server.tool(description="Suggest property-based testing")
def property_testing_tool(code: str) -> dict[str, Any]:
    """Suggest property-based testing strategies using Hypothesis."""
    return advanced_testing.suggest_property_based_tests(code)

# Version Control System Tools
@mcp_server.tool(description="Analyze Git repository")
def analyze_git_tool(repo_path: str = ".") -> dict[str, Any]:
    """Perform comprehensive Git repository analysis."""
    return vcs_integration.analyze_git_repository(repo_path)

@mcp_server.tool(description="Suggest Git workflow")
def suggest_workflow_tool(project_type: str = "general", team_size: int = 1) -> dict[str, Any]:
    """Suggest optimal Git workflow based on project characteristics."""
    return vcs_integration.suggest_git_workflow(project_type, team_size)

@mcp_server.tool(description="Generate Git hooks")
def generate_hooks_tool(hook_types: list[str]) -> dict[str, Any]:
    """Generate Git hooks for code quality and automation."""
    return vcs_integration.generate_git_hooks(hook_types)

@mcp_server.tool(description="Analyze code changes")
def analyze_changes_tool(since_ref: str = "HEAD~10") -> dict[str, Any]:
    """Analyze code changes and suggest review focus areas."""
    return vcs_integration.analyze_code_changes(since_ref)

@mcp_server.tool(description="Git bisect helper")
def git_bisect_tool(error_description: str, last_known_good: str = "") -> dict[str, Any]:
    """Suggest Git bisect strategy for finding problematic commits."""
    return vcs_integration.suggest_git_bisect_strategy(error_description, last_known_good)

# Superior Data Format Tools
@mcp_server.tool(description="Validate YAML with expert-level error detection and repair suggestions")
def validate_yaml_tool(content: str) -> dict[str, Any]:
    """Comprehensive YAML validation with advanced error detection and style analysis."""
    return data_formats.validate_yaml(content)

@mcp_server.tool(description="Validate JSON with expert-level error detection and optimization suggestions")
def validate_json_tool(content: str) -> dict[str, Any]:
    """Comprehensive JSON validation with performance analysis and security checks."""
    return data_formats.validate_json(content)

@mcp_server.tool(description="Automatically repair common YAML syntax and formatting issues")
def repair_yaml_tool(content: str) -> dict[str, Any]:
    """Intelligently repair YAML syntax errors, indentation issues, and formatting problems."""
    return data_formats.repair_yaml(content)

@mcp_server.tool(description="Automatically repair common JSON syntax issues")
def repair_json_tool(content: str) -> dict[str, Any]:
    """Intelligently repair JSON syntax errors like trailing commas, unquoted keys, etc."""
    return data_formats.repair_json(content)

@mcp_server.tool(description="Format YAML with consistent style and best practices")
def format_yaml_tool(content: str, indent: int = 2, width: int = 80) -> dict[str, Any]:
    """Format YAML with professional styling and consistent indentation."""
    return data_formats.format_yaml(content, indent, width)

@mcp_server.tool(description="Format JSON with consistent style and indentation")
def format_json_tool(content: str, indent: int = 2, sort_keys: bool = False) -> dict[str, Any]:
    """Format JSON with professional styling and optional key sorting."""
    return data_formats.format_json(content, indent, sort_keys)

@mcp_server.tool(description="Convert YAML to JSON format")
def convert_yaml_to_json_tool(yaml_content: str, indent: int = 2) -> dict[str, Any]:
    """Convert YAML content to properly formatted JSON."""
    return data_formats.convert_yaml_to_json(yaml_content, indent)

@mcp_server.tool(description="Convert JSON to YAML format")
def convert_json_to_yaml_tool(json_content: str, indent: int = 2) -> dict[str, Any]:
    """Convert JSON content to properly formatted YAML."""
    return data_formats.convert_json_to_yaml(json_content, indent)

@mcp_server.tool(description="Validate data against JSON schema")
def validate_with_schema_tool(data_content: str, schema_content: str, data_format: str = "json") -> dict[str, Any]:
    """Validate JSON/YAML data against a JSON schema with detailed error reporting."""
    return data_formats.validate_with_schema(data_content, schema_content, data_format)

@mcp_server.tool(description="Detect data format and analyze structure")
def detect_format_tool(content: str) -> dict[str, Any]:
    """Intelligently detect whether content is JSON, YAML, or other format with confidence scoring."""
    return data_formats.detect_format(content)

@mcp_server.tool(description="Compare two data structures and highlight differences")
def compare_data_structures_tool(content1: str, content2: str, format1: str = "auto", format2: str = "auto") -> dict[str, Any]:
    """Compare two data structures (JSON/YAML) and provide detailed difference analysis."""
    return data_formats.compare_data_structures(content1, content2, format1, format2)

# Advanced Data Processing Tools (Anthropic-style structured output)
@mcp_server.tool(description="Process JSON with Claude-style schema enforcement and consistency")
def advanced_json_processing_tool(content: str, schema: dict[str, Any] | None = None, template: str | None = None, strict_mode: bool = True) -> dict[str, Any]:
    """Advanced JSON processing with schema enforcement following Anthropic's tool_choice patterns."""
    return advanced_data_processing.process_json_with_schema_enforcement(content, schema, template, strict_mode)

@mcp_server.tool(description="Process YAML with template enforcement and consistency control")
def advanced_yaml_processing_tool(content: str, template: str | None = None, preserve_comments: bool = False, strict_formatting: bool = True) -> dict[str, Any]:
    """Advanced YAML processing with template enforcement and Claude-level consistency."""
    return advanced_data_processing.process_yaml_with_template_enforcement(content, template, preserve_comments, strict_formatting)

@mcp_server.tool(description="Generate structured output with enforced consistency and validation")
def structured_output_generation_tool(data: str, output_format: str = "json", template: str | None = None, schema: dict[str, Any] | None = None, consistency_mode: str = "strict_json") -> dict[str, Any]:
    """Generate structured output implementing Anthropic's advanced consistency patterns."""
    return advanced_data_processing.generate_structured_output(data, output_format, template, schema, consistency_mode)

@mcp_server.tool(description="Batch convert multiple data structures with enterprise-grade processing")
def batch_format_conversion_tool(inputs: list[dict[str, Any]], target_format: str = "json", apply_templates: bool = True, validate_schemas: bool = True) -> dict[str, Any]:
    """Batch convert multiple data structures with validation, templating, and consistency enforcement."""
    return advanced_data_processing.batch_convert_formats(inputs, target_format, apply_templates, validate_schemas)

@http_app.post("/run_code")
@log_http_request("run_code")
async def http_run_code(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    result = run_code.run_python(code)
    return JSONResponse(content=result)

@http_app.post("/lint_code")
@log_http_request("lint_code")
async def http_lint_code(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    result = lint_code.lint_python(code)
    return JSONResponse(content=result)

@http_app.post("/format_code")
@log_http_request("format_code")
async def http_format_code(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    result = format_code.format_python(code)
    return JSONResponse(content=result)

@http_app.post("/test_code")
@log_http_request("test_code")
async def http_test_code(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    result = test_code.test_python(code)
    return JSONResponse(content=result)

@http_app.post("/doc_gen")
@log_http_request("doc_gen")
async def http_doc_gen(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    result = doc_gen.generate_docs(code)
    return JSONResponse(content=result)

# AI/LLM endpoints
@http_app.post("/ai/chat")
@log_http_request("ai_chat")
async def http_ai_chat(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    prompt = data.get("prompt", "")
    model = data.get("model", "gpt-3.5-turbo")
    provider = data.get("provider", "openai")
    result = ai_tools.ai_chat(prompt, model, provider)
    return JSONResponse(content=result)

@http_app.post("/ai/embeddings")
@log_http_request("create_embeddings")
async def http_create_embeddings(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    texts = data.get("texts", [])
    model = data.get("model", "text-embedding-ada-002")
    result = ai_tools.create_embeddings(texts, model)
    return JSONResponse(content=result)

@http_app.post("/ai/vector_search")
@log_http_request("vector_search")
async def http_vector_search(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    query = data.get("query", "")
    collection = data.get("collection", "default")
    top_k = data.get("top_k", 5)
    vector_db = data.get("vector_db", "chromadb")
    result = ai_tools.vector_search(query, collection, top_k, vector_db)
    return JSONResponse(content=result)

@http_app.post("/ai/train_model")
@log_http_request("train_ml_model")
async def http_train_ml_model(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    data_code = data.get("data_code", "")
    model_type = data.get("model_type", "sklearn")
    algorithm = data.get("algorithm", "random_forest")
    result = ai_tools.train_ml_model(data_code, model_type, algorithm)
    return JSONResponse(content=result)

@http_app.post("/ai/analyze_text")
@log_http_request("analyze_text")
async def http_analyze_text(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    text = data.get("text", "")
    analysis_type = data.get("analysis_type", "sentiment")
    result = ai_tools.analyze_text(text, analysis_type)
    return JSONResponse(content=result)

@http_app.post("/ai/analyze_image")
@log_http_request("analyze_image")
async def http_analyze_image(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    image_path = data.get("image_path", "")
    analysis_type = data.get("analysis_type", "objects")
    result = ai_tools.analyze_image(image_path, analysis_type)
    return JSONResponse(content=result)

# System Intelligence endpoints
@http_app.post("/system/info")
@log_http_request("system_info")
async def http_system_info(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    result = system_intelligence.get_system_info()
    return JSONResponse(content=result)

@http_app.post("/system/code_intelligence")
@log_http_request("code_intelligence")
async def http_code_intelligence(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    analysis_type = data.get("analysis_type", "comprehensive")
    result = system_intelligence.analyze_code_intelligence(code, analysis_type)
    return JSONResponse(content=result)

@http_app.post("/system/debug")
@log_http_request("smart_debug")
async def http_smart_debug(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    error_message = data.get("error_message", "")
    result = system_intelligence.smart_debug_assistance(code, error_message)
    return JSONResponse(content=result)

@http_app.post("/system/scaffold")
@log_http_request("project_scaffold")
async def http_project_scaffold(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    project_name = data.get("project_name", "")
    project_type = data.get("project_type", "basic")
    features = data.get("features", [])
    result = system_intelligence.create_project_scaffold(project_name, project_type, features)
    return JSONResponse(content=result)

@http_app.post("/sdk/aws_upload_s3")
@log_http_request("aws_upload_s3")
async def http_aws_upload_s3(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    bucket = data.get("bucket", "")
    key = data.get("key", "")
    file_path = data.get("file_path", "")
    result = sdk_integrations.aws_upload_s3(bucket, key, file_path)
    return JSONResponse(content=result)

@http_app.post("/sdk/gcp_list_bucket")
@log_http_request("gcp_list_bucket")
async def http_gcp_list_bucket(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    bucket = data.get("bucket", "")
    result = sdk_integrations.gcp_list_bucket(bucket)
    return JSONResponse(content=result)

@http_app.post("/sdk/azure_download_blob")
@log_http_request("azure_download_blob")
async def http_azure_download_blob(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    container = data.get("container", "")
    blob_name = data.get("blob_name", "")
    download_path = data.get("download_path", "")
    result = sdk_integrations.azure_download_blob(container, blob_name, download_path)
    return JSONResponse(content=result)

# Advanced Code Analysis endpoints
@http_app.post("/analysis/type_check")
@log_http_request("type_check")
async def http_type_check(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    python_version = data.get("python_version", "3.12")
    result = advanced_code_analysis.type_check_code(code, python_version)
    return JSONResponse(content=result)

@http_app.post("/analysis/security_scan")
@log_http_request("security_scan")
async def http_security_scan(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    confidence_level = data.get("confidence_level", "medium")
    result = advanced_code_analysis.security_scan(code, confidence_level)
    return JSONResponse(content=result)

@http_app.post("/analysis/dependency_audit")
@log_http_request("dependency_audit")
async def http_dependency_audit(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    requirements_content = data.get("requirements_content", "")
    result = advanced_code_analysis.audit_dependencies(requirements_content)
    return JSONResponse(content=result)

@http_app.post("/analysis/code_completion")
@log_http_request("code_completion")
async def http_code_completion(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    cursor_position = data.get("cursor_position", -1)
    result = advanced_code_analysis.intelligent_code_completion(code, cursor_position)
    return JSONResponse(content=result)

@http_app.post("/analysis/modern_features")
@log_http_request("modern_features")
async def http_modern_features(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    result = advanced_code_analysis.analyze_modern_python_features(code)
    return JSONResponse(content=result)

# Smart Refactoring endpoints
@http_app.post("/refactor/smart_refactor")
@log_http_request("smart_refactor")
async def http_smart_refactor(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    refactor_type = data.get("refactor_type", "all")
    result = smart_refactoring.smart_refactor(code, refactor_type)
    return JSONResponse(content=result)

@http_app.post("/refactor/detect_smells")
@log_http_request("detect_smells")
async def http_detect_smells(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    result = smart_refactoring.detect_code_smells(code)
    return JSONResponse(content=result)

@http_app.post("/refactor/backward_compatibility")
@log_http_request("backward_compatibility")
async def http_backward_compatibility(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    code = data.get("code", "")
    target_version = data.get("target_version", "3.8")
    result = smart_refactoring.check_backward_compatibility(code, target_version)
    return JSONResponse(content=result)

# Superior Data Format HTTP endpoints
@http_app.post("/data/validate_yaml")
@log_http_request("validate_yaml")
async def http_validate_yaml(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content = data.get("content", "")
    result = data_formats.validate_yaml(content)
    return JSONResponse(content=result)

@http_app.post("/data/validate_json")
@log_http_request("validate_json")
async def http_validate_json(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content = data.get("content", "")
    result = data_formats.validate_json(content)
    return JSONResponse(content=result)

@http_app.post("/data/repair_yaml")
@log_http_request("repair_yaml")
async def http_repair_yaml(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content = data.get("content", "")
    result = data_formats.repair_yaml(content)
    return JSONResponse(content=result)

@http_app.post("/data/repair_json")
@log_http_request("repair_json")
async def http_repair_json(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content = data.get("content", "")
    result = data_formats.repair_json(content)
    return JSONResponse(content=result)

@http_app.post("/data/format_yaml")
@log_http_request("format_yaml")
async def http_format_yaml(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content = data.get("content", "")
    indent = data.get("indent", 2)
    width = data.get("width", 80)
    result = data_formats.format_yaml(content, indent, width)
    return JSONResponse(content=result)

@http_app.post("/data/format_json")
@log_http_request("format_json")
async def http_format_json(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content = data.get("content", "")
    indent = data.get("indent", 2)
    sort_keys = data.get("sort_keys", False)
    result = data_formats.format_json(content, indent, sort_keys)
    return JSONResponse(content=result)

@http_app.post("/data/convert_yaml_to_json")
@log_http_request("convert_yaml_to_json")
async def http_convert_yaml_to_json(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    yaml_content = data.get("yaml_content", "")
    indent = data.get("indent", 2)
    result = data_formats.convert_yaml_to_json(yaml_content, indent)
    return JSONResponse(content=result)

@http_app.post("/data/convert_json_to_yaml")
@log_http_request("convert_json_to_yaml")
async def http_convert_json_to_yaml(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    json_content = data.get("json_content", "")
    indent = data.get("indent", 2)
    result = data_formats.convert_json_to_yaml(json_content, indent)
    return JSONResponse(content=result)

@http_app.post("/data/validate_with_schema")
@log_http_request("validate_with_schema")
async def http_validate_with_schema(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    data_content = data.get("data_content", "")
    schema_content = data.get("schema_content", "")
    data_format = data.get("data_format", "json")
    result = data_formats.validate_with_schema(data_content, schema_content, data_format)
    return JSONResponse(content=result)

@http_app.post("/data/detect_format")
@log_http_request("detect_format")
async def http_detect_format(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content = data.get("content", "")
    result = data_formats.detect_format(content)
    return JSONResponse(content=result)

@http_app.post("/data/compare_structures")
@log_http_request("compare_structures")
async def http_compare_structures(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content1 = data.get("content1", "")
    content2 = data.get("content2", "")
    format1 = data.get("format1", "auto")
    format2 = data.get("format2", "auto")
    result = data_formats.compare_data_structures(content1, content2, format1, format2)
    return JSONResponse(content=result)

# Advanced Data Processing HTTP endpoints (Anthropic-style)
@http_app.post("/data/advanced_json_processing")
@log_http_request("advanced_json_processing")
async def http_advanced_json_processing(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content = data.get("content", "")
    schema = data.get("schema")
    template = data.get("template")
    strict_mode = data.get("strict_mode", True)
    result = advanced_data_processing.process_json_with_schema_enforcement(content, schema, template, strict_mode)
    return JSONResponse(content=result)

@http_app.post("/data/advanced_yaml_processing")
@log_http_request("advanced_yaml_processing")
async def http_advanced_yaml_processing(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    content = data.get("content", "")
    template = data.get("template")
    preserve_comments = data.get("preserve_comments", False)
    strict_formatting = data.get("strict_formatting", True)
    result = advanced_data_processing.process_yaml_with_template_enforcement(content, template, preserve_comments, strict_formatting)
    return JSONResponse(content=result)

@http_app.post("/data/structured_output_generation")
@log_http_request("structured_output_generation")
async def http_structured_output_generation(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    input_data = data.get("data", "")
    output_format = data.get("output_format", "json")
    template = data.get("template")
    schema = data.get("schema")
    consistency_mode = data.get("consistency_mode", "strict_json")
    result = advanced_data_processing.generate_structured_output(input_data, output_format, template, schema, consistency_mode)
    return JSONResponse(content=result)

@http_app.post("/data/batch_format_conversion")
@log_http_request("batch_format_conversion")
async def http_batch_format_conversion(
    request: Request,
    auth_info: dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    data = await request.json()
    inputs = data.get("inputs", [])
    target_format = data.get("target_format", "json")
    apply_templates = data.get("apply_templates", True)
    validate_schemas = data.get("validate_schemas", True)
    result = advanced_data_processing.batch_convert_formats(inputs, target_format, apply_templates, validate_schemas)
    return JSONResponse(content=result)


def get_deployment_config():
    """Get deployment configuration for Railway and other platforms"""
    return {
        "host": "0.0.0.0" if os.getenv("ENVIRONMENT") == "production" else "localhost",
        "port": int(os.getenv("HTTP_PORT", os.getenv("PORT", 8080))),
        "reload": os.getenv("ENVIRONMENT") != "production",
        "log_level": "info"
    }


def run_http_server():
    """Run HTTP server with appropriate configuration"""
    config = get_deployment_config()
    uvicorn.run(
        http_app, 
        host=config["host"], 
        port=config["port"],
        log_level=config["log_level"],
        reload=config["reload"]
    )


def main():
    """Main function to run both HTTP and MCP servers."""
    try:
        config = get_deployment_config()
        
        # Check if we're running in production (Railway/cloud)
        if os.getenv("ENVIRONMENT") == "production":
            logger.info("🚀 Starting Python MCP Server in PRODUCTION mode")
            logger.info(f"   Host: {config['host']}")
            logger.info(f"   Port: {config['port']}")
            logger.info(f"   Environment: {os.getenv('ENVIRONMENT')}")
            logger.info("📡 Protocols: HTTP REST API + WebSocket MCP")
            
            # Production: run HTTP server with WebSocket MCP support
            uvicorn.run(
                "mcp_server.server:http_app",
                host=config["host"],
                port=config["port"],
                log_level=config["log_level"]
            )
        else:
            # Development mode: run both HTTP and MCP servers
            logger.info("🔧 Starting Python MCP Server in DEVELOPMENT mode")
            logger.info("📡 Protocols: HTTP REST API + WebSocket MCP + stdin/stdout MCP")
            
            # Run HTTP server in a separate thread
            http_thread = threading.Thread(target=run_http_server, daemon=True)
            http_thread.start()
            logger.info(f"Started HTTP server on http://{config['host']}:{config['port']}")

            # Run MCP server on stdin/stdout
            logger.info("Starting MCP server...")
            mcp_server.run()
            
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
