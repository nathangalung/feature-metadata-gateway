FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency files and README.md for build metadata
COPY pyproject.toml uv.lock requirements.txt README.md ./

# Install dependencies (no project code yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Now copy the rest of the project
COPY . .

# Install project in non-editable mode (for prod)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -m -r -g appuser appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/app /app/app
COPY --from=builder --chown=appuser:appuser /app/data /app/data
COPY --from=builder --chown=appuser:appuser /app/logs /app/logs
COPY --from=builder --chown=appuser:appuser /app/pyproject.toml /app/
COPY --from=builder --chown=appuser:appuser /app/requirements.txt /app/
COPY --from=builder --chown=appuser:appuser /app/uv.lock /app/
COPY --from=builder --chown=appuser:appuser /app/README.md /app/

# Ensure home and cache directories exist and are owned by appuser
RUN mkdir -p /home/appuser/.cache/uv && chown -R appuser:appuser /home/appuser

ENV HOME=/home/appuser
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir -p /app/data /app/logs && chown appuser:appuser /app/data /app/logs

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]