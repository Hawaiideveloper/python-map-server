
# Python MCP Server Architecture & Workflow

## Overview
This MCP server provides a standard JSON-RPC interface compliant with the Model Context Protocol (MCP). It also exposes an HTTP REST API bridge to support LLMs that do not support MCP natively.

## Components

### MCP Server (src/mcp_server/server.py)
- Listens on stdin/stdout for JSON-RPC MCP messages.
- Also runs FastAPI HTTP server on port 8080.
- Dispatches requests to individual tools.

### Tools (src/mcp_server/tools/)
- `run_code.py`: Executes Python code in a sandboxed subprocess.
- `lint_code.py`: Runs `ruff` to lint Python code.
- `format_code.py`: Runs `black` to format Python code.
- `test_code.py`: Auto-generates and runs pytest tests.
- `doc_gen.py`: Generates docstrings and documentation.
- `sdk_integrations.py`: Provides cloud SDK helper functions for AWS, GCP, Azure.

### Utils (src/mcp_server/utils/)
- `sandbox.py`: Implements safe Python code execution environment.
- `fs.py`: File system utilities for reading/writing project files.

### CLI (src/cli.py)
- Entry point to run server in local or shared mode.

## Workflow

1. LLM client connects via MCP or HTTP REST.
2. Client sends commands (e.g., `run_code`, `lint_code`).
3. Server processes commands, executes tools, and returns results.
4. Continuous integration via GitHub Actions ensures code quality and builds Docker image.

## Extensibility

- New tools can be added under `tools/` and registered in the server.
- Additional SDK integrations can be added in `sdk_integrations.py`.
- Server supports multi-user deployment by switching config modes.

