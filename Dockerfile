
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

COPY src /app/src
COPY .env.example /app/.env.example

ENV PYTHONPATH=/app/src

EXPOSE 8080

CMD ["python", "-m", "mcp_server.server"]
