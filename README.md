# FastAPI Blog — API-first (Milestone 1A)

Single-container **FastAPI Blog**. This repo currently includes **API-only** (no frontend yet) with a `/api/health` endpoint and Dockerized runtime.

## Quick Start

```bash
# build
docker build -t fastapi-blog-api:dev .

# run on default port 8000
docker run --rm -p 8000:8000 --name fastapi-blog-api fastapi-blog-api:dev

# healthcheck
curl -s http://localhost:8000/api/health
```
