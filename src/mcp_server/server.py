
import asyncio
import json
import sys
import threading
from typing import Dict, Any
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
import uvicorn
from mcp.server.fastmcp import FastMCP

from mcp_server.tools import (
    run_code,
    lint_code,
    format_code,
    test_code,
    doc_gen,
    sdk_integrations,
    ai_tools,
    system_intelligence,
)
from mcp_server.utils.auth import authenticate_request, check_rate_limit
from mcp_server.utils.logging import log_http_request

import os

# Create FastMCP app
app = FastMCP("python-mcp-server")

# Register MCP tools using decorators
@app.tool
def run_python(code: str) -> Dict[str, Any]:
    """Execute Python code safely using a subprocess and return output."""
    return run_code.run_python(code)

@app.tool  
def lint_python(code: str) -> Dict[str, Any]:
    """Lint Python code using ruff and return analysis."""
    return lint_code.lint_python(code)

@app.tool
def format_python(code: str) -> Dict[str, Any]:
    """Format Python code using black and return formatted result."""
    return format_code.format_python(code)

@app.tool
def test_python(code: str) -> Dict[str, Any]:
    """Test Python code using pytest and return results."""
    return test_code.test_python(code)

@app.tool
def generate_docs(code: str) -> Dict[str, Any]:
    """Generate documentation for Python code."""
    return doc_gen.generate_docs(code)

# HTTP API bridge using FastAPI
http_app = FastAPI(title="Python MCP Server API", version="0.1.0")

@http_app.post("/run_code")
@log_http_request("run_code")
async def http_run_code(
    request: Request,
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
):
    check_rate_limit(request)
    result = system_intelligence.get_system_info()
    return JSONResponse(content=result)

@http_app.post("/system/code_intelligence")
@log_http_request("code_intelligence")
async def http_code_intelligence(
    request: Request,
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    auth_info: Dict[str, Any] = Depends(authenticate_request)
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
    # Run HTTP server in a separate thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Run MCP server on stdin/stdout
    app.run()

if __name__ == "__main__":
    main()
