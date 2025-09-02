# FastAPI Blog

## Overview

- Single Docker container running a FastAPI API.
- Current scope: API only with a /api/health endpoint.
- SQLite by default for local use; Postgres support will be added in later milestones.
- Designed to later sit behind Nginx Proxy Manager.

## Requirements

- Docker installed and running.
- Optional: docker compose for simpler environment and port overrides.

## Quick Start (Docker)

    docker build -t fastapi-blog-api:dev .
    docker run --rm -p 8000:8000 --name fastapi-blog-api fastapi-blog-api:dev

- Open in a browser: http://localhost:8000/api/health

## Health Check

- The health endpoint returns a small JSON payload confirming the app is running.
- Example:
  curl -s http://localhost:8000/api/health

## Custom Ports (docker compose)

- Create a .env file with values like:
  PORT=8081
  HOST_PORT=18000
- Start the container:
  docker compose up --build
- Test:
  curl -s http://localhost:18000/api/health

## Common Commands

- Build image:
  docker build -t fastapi-blog-api:dev .
- Run (default ports):
  docker run --rm -p 8000:8000 --name fastapi-blog-api fastapi-blog-api:dev
- Stop and remove the container:
  docker stop fastapi-blog-api

## Git Basics

- Stage, commit, and push:
  git add -A
  git commit -m "Update README and milestone 1A"
  git push

## Milestones

- 1A: API-only container with healthcheck.
- 1B: Add frontend scaffold (React islands) to the same image.
- 1C: Static files and templates wiring; prepare for Nginx Proxy Manager.
- Later: Postgres configuration, admin routes, CSP/security, and rolling updates.
