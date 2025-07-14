# Build base image
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock requirements.txt README.md ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy project code
COPY . .

# Install project (prod)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# System setup
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -m -r -g appuser appuser

WORKDIR /app

# Copy built artifacts
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/app /app/app
COPY --from=builder --chown=appuser:appuser /app/tests /app/tests
COPY --from=builder --chown=appuser:appuser /app/data /app/data
COPY --from=builder --chown=appuser:appuser /app/logs /app/logs
COPY --from=builder --chown=appuser:appuser /app/pyproject.toml /app/
COPY --from=builder --chown=appuser:appuser /app/requirements.txt /app/
COPY --from=builder --chown=appuser:appuser /app/uv.lock /app/
COPY --from=builder --chown=appuser:appuser /app/README.md /app/

# Ensure directories and permissions
RUN mkdir -p /home/appuser/.cache/uv && chown -R appuser:appuser /home/appuser
RUN mkdir -p /app/data /app/logs && chown appuser:appuser /app/data /app/logs
RUN chown -R appuser:appuser /app

ENV HOME=/home/appuser
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]