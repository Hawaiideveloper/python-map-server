
import asyncio
import json
import sys
import threading
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from mcp.server import Server

from mcp_server.tools import (
    run_code,
    lint_code,
    format_code,
    test_code,
    doc_gen,
    sdk_integrations,
)

import os

app = Server()

# Register MCP tools
app.register_tool(run_code.run_python)
app.register_tool(lint_code.lint_python)
app.register_tool(format_code.format_python)
app.register_tool(test_code.test_python)
app.register_tool(doc_gen.generate_docs)
app.register_tool(sdk_integrations.aws_upload_s3)
app.register_tool(sdk_integrations.gcp_list_bucket)
app.register_tool(sdk_integrations.azure_download_blob)

# HTTP API bridge using FastAPI
http_app = FastAPI()

@http_app.post("/run_code")
async def http_run_code(request: Request):
    data = await request.json()
    code = data.get("code", "")
    result = run_code.run_python(code)
    return JSONResponse(content=result)

@http_app.post("/lint_code")
async def http_lint_code(request: Request):
    data = await request.json()
    code = data.get("code", "")
    result = lint_code.lint_python(code)
    return JSONResponse(content=result)

@http_app.post("/format_code")
async def http_format_code(request: Request):
    data = await request.json()
    code = data.get("code", "")
    result = format_code.format_python(code)
    return JSONResponse(content=result)

@http_app.post("/test_code")
async def http_test_code(request: Request):
    data = await request.json()
    code = data.get("code", "")
    result = test_code.test_python(code)
    return JSONResponse(content=result)

@http_app.post("/doc_gen")
async def http_doc_gen(request: Request):
    data = await request.json()
    code = data.get("code", "")
    result = doc_gen.generate_docs(code)
    return JSONResponse(content=result)

@http_app.post("/sdk/aws_upload_s3")
async def http_aws_upload_s3(request: Request):
    data = await request.json()
    bucket = data.get("bucket", "")
    key = data.get("key", "")
    file_path = data.get("file_path", "")
    result = sdk_integrations.aws_upload_s3(bucket, key, file_path)
    return JSONResponse(content=result)

@http_app.post("/sdk/gcp_list_bucket")
async def http_gcp_list_bucket(request: Request):
    data = await request.json()
    bucket = data.get("bucket", "")
    result = sdk_integrations.gcp_list_bucket(bucket)
    return JSONResponse(content=result)

@http_app.post("/sdk/azure_download_blob")
async def http_azure_download_blob(request: Request):
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
