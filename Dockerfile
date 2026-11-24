# ─────────────────────────────────────────
#  Stage 1: builder
# ─────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Paquetes del sistema requeridos por WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-xlib-2.0-0 \
        libcairo2 \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies in an isolated layer
COPY requirements.txt .
# Versiones fijadas en requirements.txt; solo wheels (sin ejecutar setup.py).
RUN pip install --no-cache-dir --only-binary :all: --prefix=/install -r requirements.txt


# ─────────────────────────────────────────
#  Stage 2: runtime
# ─────────────────────────────────────────
FROM python:3.12-slim

# WeasyPrint necesita estas libs también en tiempo de ejecución
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-xlib-2.0-0 \
        libcairo2 \
        libffi8 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY . .

# Set ownership
RUN chown -R appuser:appgroup /app
RUN sed -i 's/\r$//' /app/scripts/entrypoint.sh
USER appuser

# Runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8000)}/health')"

# Start the application via entrypoint script
CMD ["sh", "/app/scripts/entrypoint.sh"]