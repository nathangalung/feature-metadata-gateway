FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Copy only dependency files first for better caching
COPY pyproject.toml uv.lock requirements.txt ./

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
    && groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy only the necessary project files (not .venv)
COPY --from=builder --chown=appuser:appuser /app/app /app/app
COPY --from=builder --chown=appuser:appuser /app/data /app/data
COPY --from=builder --chown=appuser:appuser /app/logs /app/logs
COPY --from=builder --chown=appuser:appuser /app/pyproject.toml /app/
COPY --from=builder --chown=appuser:appuser /app/requirements.txt /app/
COPY --from=builder --chown=appuser:appuser /app/uv.lock /app/

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