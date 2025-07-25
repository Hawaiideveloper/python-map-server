
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock* /app/

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false && poetry install --only=main

COPY src /app/src
COPY logs/ /app/logs/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV ENVIRONMENT=production

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Railway sets PORT automatically, but default to 8000
EXPOSE ${PORT:-8000}

CMD ["python", "-m", "mcp_server.server"]
