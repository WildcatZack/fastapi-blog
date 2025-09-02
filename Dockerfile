FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends curl tini && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code (keep it under /app/app)
COPY app ./app

# Ensure directories exist and are writable by appuser
RUN mkdir -p /app/app/static && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["sh","-lc","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
