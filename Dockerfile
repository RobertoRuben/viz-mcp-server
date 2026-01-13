FROM python:3.13-slim AS base

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential curl \
    && pip install --no-cache-dir uv \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv pip install --system --no-cache-dir .

COPY src/ ./src/

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 3031

CMD ["uv", "run", "fastmcp", "run", "src/app/main.py:mcp", "--transport", "sse", "--host", "0.0.0.0", "--port", "3031"]