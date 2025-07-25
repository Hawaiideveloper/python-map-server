
# Python MCP Server

This repository contains a full-featured Python MCP (Model Context Protocol) server designed to:

- Execute Python code safely with sandboxing
- Enforce best practices: linting (ruff), formatting (black), testing (pytest), and documentation (Sphinx/mkdocs)
- Integrate AWS, GCP, and Azure SDKs with pre-built examples
- Provide JSON-RPC MCP interface compatible with OpenAI, Claude, and other LLM clients
- Provide HTTP REST bridge for LLMs like Grok, Gemini, and Ollama
- Support local single-user mode and easy upgrade to multi-user shared server mode
- Full CI/CD via GitHub Actions (lint, test, docker build)

## Installation

### Local install via Poetry (recommended)

```bash
git clone <repo-url>
cd python-mcp-server
poetry install
poetry run python -m mcp_server.server
```

### Install via pip

```bash
pip install .
python -m mcp_server.server
```

### Using Docker

Build image:

```bash
docker build -t python-mcp-server .
```

Run container (default local mode):

```bash
docker run -p 8080:8080 python-mcp-server
```

## Configuration

Copy `.env.example` to `.env` and fill in your cloud provider credentials:

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=your_region

GCP_PROJECT=your_project
GCP_CREDENTIALS_PATH=path_to_your_gcp_credentials.json

AZURE_STORAGE_CONNECTION_STRING=your_connection_string
```

## Usage

- MCP JSON-RPC server listens on stdin/stdout for compatible LLM clients (OpenAI MCP, Claude)
- HTTP REST API available at port 8080 for Grok, Gemini, Ollama, and others

## Tools Provided

- `run_code`: Execute Python safely
- `lint_code`: Lint Python code using ruff
- `format_code`: Format code using black
- `test_code`: Auto-generate and run pytest unit tests
- `doc_gen`: Generate docstrings and project documentation
- `sdk_integrations`: Cloud SDK helpers for AWS, GCP, Azure with examples

## Contributing

Pull requests welcome. Please ensure code is linted and tested.

## License

MIT License
