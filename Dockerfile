# Multi-stage Dockerfile for high-performance Python MCP Server
# Optimized for production deployment with minimal attack surface

# Stage 1: Builder
FROM python:3.12-slim as builder

# Set build arguments
ARG POETRY_VERSION=1.7.1
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==$POETRY_VERSION

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies and create virtual environment
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Stage 2: Production
FROM python:3.12-slim as production

# Set production arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Add metadata labels
LABEL org.opencontainers.image.title="Python MCP Server" \
      org.opencontainers.image.description="High-performance Python Model Context Protocol server" \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.vendor="Python MCP Server" \
      org.opencontainers.image.licenses="MIT"

# Install runtime dependencies and build tools
RUN apt-get update && apt-get install -y \
    # Required for psutil and system monitoring
    procps \
    # Required for git operations
    git \
    # Required for network operations
    curl \
    # Required for Redis connections
    redis-tools \
    # Required for building Python packages
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser -u 1000 mcpuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/usr/local/bin:$PATH" \
    ENVIRONMENT=production \
    HTTP_HOST=0.0.0.0 \
    HTTP_PORT=8080

# Copy Poetry files and install dependencies directly
COPY --chown=mcpuser:mcpuser pyproject.toml poetry.lock ./
RUN pip install poetry==1.7.1 && poetry config virtualenvs.create false && poetry install --only=main

# Set work directory
WORKDIR /app

# Copy application code
COPY --chown=mcpuser:mcpuser . .

# Create necessary directories with correct permissions
RUN mkdir -p /app/logs /app/data /app/temp /app/cache \
    && chown -R mcpuser:mcpuser /app \
    && chmod -R 755 /app

# Create docs directory for Python documentation
RUN mkdir -p /app/docs/python_manuals \
    && chown -R mcpuser:mcpuser /app/docs \
    && chmod -R 755 /app/docs

# Switch to non-root user
USER mcpuser

# Install the application
RUN python -m pip install --no-deps -e .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:$HTTP_PORT/health || exit 1

# Expose port
EXPOSE 8080

# Default command
CMD ["python", "-m", "mcp_server.server"]

# Alternative: Use Gunicorn for production (uncomment to use)
# CMD ["gunicorn", "-c", "production-config/gunicorn.conf.py", "mcp_server.server:http_app"]

# Stage 3: Development (optional)
FROM production as development

# Switch back to root for development dependencies
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    strace \
    lsof \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy development virtual environment with dev dependencies
COPY --from=builder /app/.venv /app/.venv

# Install dev dependencies
USER mcpuser
RUN /app/.venv/bin/poetry install --with dev

# Set development environment
ENV ENVIRONMENT=development \
    DEVELOPMENT_MODE=true \
    AUTO_RELOAD=true \
    LOG_LEVEL=debug

# Development command
CMD ["python", "-m", "mcp_server.server"]