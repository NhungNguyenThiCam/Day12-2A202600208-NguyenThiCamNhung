# ============================================================
# Production Dockerfile — Multi-stage Build
# Target: < 500 MB, secure, production-ready
# ============================================================

# ──────────────────────────────────────────────────────────
# STAGE 1: Builder
# Install all dependencies including build tools
# ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ──────────────────────────────────────────────────────────
# STAGE 2: Runtime
# Copy only what's needed to run the application
# ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Create non-root user for security
RUN groupadd -r agent && useradd -r -g agent -d /app agent

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/agent/.local

# Make sure pip packages are in system path
ENV PATH=/home/agent/.local/bin:$PATH

# Copy application code
COPY app/ ./app/
COPY utils/ ./utils/

# Set ownership
RUN chown -R agent:agent /app

# Switch to non-root user
USER agent

# Environment variables
ENV PATH=/home/agent/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uvicorn globally to ensure it's available
USER root
RUN pip install --no-cache-dir uvicorn[standard]==0.27.0
USER agent

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
