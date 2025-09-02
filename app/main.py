from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.__version__ import VERSION as APP_VERSION
from app.middleware.security import SecurityHeadersMiddleware
from app.settings import settings
from app.routers.health import router as health_router
from app.routers.config import router as config_router

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="FastAPI Blog API", version=APP_VERSION)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS (disabled unless CORS_ALLOW_ORIGINS is set)
origins = settings.cors_origins
if origins:
    # If credentials are allowed, '*' is not permitted by browsers; require explicit origins.
    allow_origins = origins if settings.CORS_ALLOW_CREDENTIALS or origins != ["*"] else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
        expose_headers=["X-Request-ID"],  # handy later when we add request IDs
    )

# Static files
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(config_router, prefix="/api", tags=["config"])

# Home page (server-rendered with Jinja2)
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "FastAPI Blog",
            "subtitle": "Server-rendered homepage (React island enabled)",
        },
    )
