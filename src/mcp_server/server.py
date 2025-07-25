
"""
Enhanced Python MCP Server with AI/LLM integration and comprehensive tooling.

This module implements the main MCP server with JSON-RPC protocol support,
HTTP REST API bridge, security features, and comprehensive tool registration.
"""

import sys
import threading
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server.fastmcp.server import FastMCP

from mcp_server.config import DEVELOPMENT_MODE
from mcp_server.tools import (
    ai_tools,
    doc_gen,
    format_code,
    lint_code,
    run_code,
    sdk_integrations,
    system_intelligence,
    test_code,
)
from mcp_server.utils.auth import authenticate_request, check_rate_limit
from mcp_server.utils.logging import log_http_request, setup_logger

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add CORS middleware
http_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEVELOPMENT_MODE else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def run_http_server():
    uvicorn.run(http_app, host="0.0.0.0", port=8080)


def main():
    """Main function to run both HTTP and MCP servers."""
    try:
        # Run HTTP server in a separate thread
        http_thread = threading.Thread(target=run_http_server, daemon=True)
        http_thread.start()
        logger.info("Started HTTP server on http://0.0.0.0:8080")

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
