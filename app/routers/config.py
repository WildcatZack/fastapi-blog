from fastapi import APIRouter
from app.settings import settings

router = APIRouter()

@router.get("/config")
async def get_config():
    # Never return DATABASE_URL or any secrets
    return settings.public_dict()
