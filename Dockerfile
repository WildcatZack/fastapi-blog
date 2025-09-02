FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root (optional but good practice)
RUN useradd -m appuser

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends curl tini && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app ./app

USER appuser

EXPOSE 8000
ENTRYPOINT ["/usr/bin/tini","--"]
# PORT is configurable via env; default 8000. Host 0.0.0.0 is required in containers.
CMD ["sh","-lc","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
