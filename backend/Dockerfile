# ==============================================================================
# Multi-Stage Optimized Slim Dockerfile for Wealify Backend (FastAPI)
# Target: Render, Cloud Run, Docker Compose
# ==============================================================================

# ── Stage 1: Builder (Dependency Compilation & Virtualenv) ───────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies for compiling binary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create virtualenv, install dependencies, and purge all installation caches
COPY backend/requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    # Remove compiled bytecode and temporary package caches
    find /opt/venv -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/venv -type f -name "*.pyc" -delete && \
    find /opt/venv -type f -name "*.pyo" -delete && \
    rm -rf /root/.cache /root/.cargo

# ── Stage 2: Final Runner (Ultra-Slim Production Runtime) ────────────────────
FROM python:3.11-slim AS runner

# Production Python runtime environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    ML_ROOT=/app

WORKDIR /app/backend

# Install minimal runtime dependencies (curl for healthchecks only) & clean apt caches
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/apt/* \
    && useradd --create-home --home-dir /home/appuser --shell /bin/bash -u 10001 appuser

# Copy clean virtual environment from builder stage (no compiler or pip cache bloat)
COPY --from=builder /opt/venv /opt/venv

# Copy application source code (repo root -> /app, so uvicorn runs from /app/backend)
COPY --chown=appuser:appuser . /app

# Purge any local Python caches and configure non-root ownership
RUN find /app -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true && \
    find /app -type f -name "*.pyc" -delete && \
    chown -R appuser:appuser /app

# Switch to unprivileged user
USER appuser

EXPOSE 8000

# Healthcheck for container orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT:-8000}/api/health || exit 1

# Start Uvicorn from /app/backend (working dir) where src/ lives
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
