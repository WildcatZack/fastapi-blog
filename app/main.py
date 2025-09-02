from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers.health import router as health_router
from app.routers.config import router as config_router  # NEW

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="FastAPI Blog API", version="0.2.0")  # bumped

# Static files
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(config_router, prefix="/api", tags=["config"])  # NEW

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
