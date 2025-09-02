from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers.health import router as health_router

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="FastAPI Blog API", version="0.0.2")

# Static files (directory exists in repo; no mkdir at runtime)
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Keep the API health router
app.include_router(health_router, prefix="/api", tags=["health"])

# Home page (server-rendered with Jinja2)
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "FastAPI Blog",
            "subtitle": "Server-rendered homepage (React comes next)",
        },
    )
