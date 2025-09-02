# --- Stage 1: Build React island with Vite ---
FROM node:20-alpine AS frontend

WORKDIR /build

# Install deps with cache-friendly layers
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund

# Copy only what's needed for the build
COPY tsconfig.json vite.config.ts ./
COPY webui ./webui

# Outputs to /build/app/static/assets/main.js (per vite.config.ts)
RUN npm run build


# --- Stage 2: Python runtime ---
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root user for safety
RUN useradd -m -u 1000 appuser

WORKDIR /app

# System deps (curl for healthchecks, tini for clean PID1)
RUN apt-get update && apt-get install -y --no-install-recommends curl tini && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app ./app

# Bring in built static assets from the frontend stage
COPY --from=frontend /build/app/static ./app/static

# Ensure permissions
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# --- Container-level healthcheck (respects PORT env, default 8000) ---
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD ["sh","-lc","curl -fsS http://127.0.0.1:${PORT:-8000}/api/health >/dev/null || exit 1"]

ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["sh","-lc","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
