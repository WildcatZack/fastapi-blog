from fastapi import APIRouter
from app.settings import settings

router = APIRouter()

@router.get("/health")
async def health():
  return {
      "status": "ok",
      "env": settings.APP_ENV,
      "message": "FastAPI Blog API alive",
  }
