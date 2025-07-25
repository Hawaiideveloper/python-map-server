#!/bin/bash

# Python MCP Server Setup Script
# This script sets up the development environment with Poetry

set -e  # Exit on any error

echo "🚀 Setting up Python MCP Server with Poetry..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo "✅ Poetry installed successfully"
    echo "⚠️  Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
    echo "Then re-run this script"
    exit 1
else
    echo "✅ Poetry found: $(poetry --version)"
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
required_version="3.12"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
    echo "❌ Python 3.12+ required. Found: $python_version"
    echo "Please install Python 3.12 or higher"
    exit 1
else
    echo "✅ Python version: $python_version"
fi

# Install dependencies with Poetry
echo "📦 Installing dependencies with Poetry..."
poetry install --with dev

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p models
mkdir -p chroma_db
mkdir -p temp

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
else
    echo "✅ .env file already exists"
fi

# Check if we're in a Poetry shell
if [[ "$POETRY_ACTIVE" == "1" ]]; then
    echo "✅ Already in Poetry shell"
else
    echo "🔄 Activating Poetry shell..."
    echo "Run: poetry shell"
fi

# Install additional development tools
echo "🛠️  Installing development tools..."
poetry run python -m pip install --upgrade pip

# Download spaCy language model
echo "📚 Downloading spaCy English model..."
poetry run python -m spacy download en_core_web_sm || echo "⚠️  spaCy model download failed (optional)"

# Test installation
echo "🧪 Testing installation..."
poetry run python -c "
import sys
print(f'✅ Python: {sys.version}')

# Test core imports
try:
    import mcp
    print('✅ MCP Python imported successfully')
except ImportError as e:
    print(f'❌ MCP import failed: {e}')

try:
    import numpy
    print('✅ NumPy imported successfully')
except ImportError as e:
    print(f'❌ NumPy import failed: {e}')

try:
    import pandas
    print('✅ Pandas imported successfully')
except ImportError as e:
    print(f'❌ Pandas import failed: {e}')

try:
    import torch
    print('✅ PyTorch imported successfully')
except ImportError as e:
    print(f'❌ PyTorch import failed: {e}')

try:
    import openai
    print('✅ OpenAI imported successfully')
except ImportError as e:
    print(f'❌ OpenAI import failed: {e}')

try:
    import fastapi
    print('✅ FastAPI imported successfully')
except ImportError as e:
    print(f'❌ FastAPI import failed: {e}')
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: poetry shell (if not already active)"
echo "3. Start the server: poetry run python -m mcp_server.server"
echo "4. Or run tests: poetry run pytest"
echo ""
echo "Available commands:"
echo "  poetry run ruff check .           # Lint code"
echo "  poetry run black .                # Format code"
echo "  poetry run pytest                 # Run tests"
echo "  poetry run jupyter lab             # Start Jupyter Lab"
echo "  poetry run python -m mcp_server.server  # Start server"
echo ""
echo "For more information, see the README.md file."
