from fastapi import FastAPI
from app.routers.health import router as health_router

app = FastAPI(title="FastAPI Blog API", version="0.0.1")

# Only the API router for now
app.include_router(health_router, prefix="/api", tags=["health"])
