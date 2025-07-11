# Use official uv image with Python 3.13
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Set build environment variables
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock requirements.txt ./

# Install dependencies only (no project)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Production stage
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser data/ ./data/
COPY --chown=appuser:appuser pyproject.toml ./

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create logs directory
RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

# Install project in non-editable mode
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]