
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry with specific version for consistency
RUN pip install poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry and install dependencies (exclude dev and test groups)
RUN poetry config virtualenvs.create false \
    && poetry install --without dev,test --no-interaction --no-ansi

# Copy source code
COPY src /app/src

# Create logs directory if it doesn't exist
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV ENVIRONMENT=production

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Railway sets PORT automatically, but default to 8000
EXPOSE ${PORT:-8000}

CMD ["python", "-m", "mcp_server.server"]
