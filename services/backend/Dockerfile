# ─── Stage 1: Builder ────────────────────────────────────────────────
FROM python:3.13-slim-bookworm AS builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Export requirements and install dependencies
RUN uv export --no-dev --frozen > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==22.0.0 uvicorn[standard]==0.30.0 psycopg2-binary>=2.9.10 whitenoise>=6.6.0

# ─── Stage 2: Runtime ────────────────────────────────────────────────
FROM python:3.13-slim-bookworm

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Copy entrypoint and fix permissions
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh && \
    sed -i 's/\r$//' /app/entrypoint.sh && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appgroup /app

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

# Gunicorn + Uvicorn workers (ASGI production server)
CMD ["gunicorn", "core.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
