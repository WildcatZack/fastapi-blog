import time
from typing import Literal, Tuple
from urllib.parse import urlparse

from fastapi import APIRouter, Response, status
from app.settings import settings

router = APIRouter()

@router.get("/health")
async def health():
    return {
        "status": "ok",
        "env": settings.APP_ENV,
        "message": "FastAPI Blog API alive",
    }

async def _ping_postgres(dsn: str, timeout_ms: int) -> Tuple[bool, str]:
    import asyncpg  # local import keeps driver optional
    try:
        timeout_sec = max(timeout_ms, 50) / 1000  # floor ~50ms
        conn = await asyncpg.connect(dsn=dsn, timeout=timeout_sec)
        try:
            await conn.fetchval("SELECT 1;")
        finally:
            await conn.close()
        return True, "ok"
    except Exception as e:
        return False, f"error: {type(e).__name__}"

async def _ping_sqlite(url: str, timeout_ms: int) -> Tuple[bool, str]:
    import aiosqlite  # local import keeps driver optional
    parsed = urlparse(url)
    path = parsed.path or ":memory:"
    if path.startswith("/./"):  # handle sqlite+aiosqlite:///./app.db
        path = path[1:]
    try:
        timeout_sec = max(timeout_ms, 50) / 1000
        async with aiosqlite.connect(path, timeout=timeout_sec) as db:
            await db.execute("SELECT 1;")
        return True, "ok"
    except Exception as e:
        return False, f"error: {type(e).__name__}"

async def _maybe_ping_db(dsn: str | None, timeout_ms: int) -> Tuple[Literal["skipped","ok","error"], str]:
    if not dsn:
        return "skipped", "DATABASE_URL not set"

    scheme = urlparse(dsn).scheme.lower()
    started = time.perf_counter()

    if scheme.startswith("postgres"):
        ok, msg = await _ping_postgres(dsn, timeout_ms)
    elif scheme.startswith("sqlite"):
        ok, msg = await _ping_sqlite(dsn, timeout_ms)
    else:
        return "skipped", f"unsupported scheme: {scheme}"

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    if ok:
        return "ok", f"{msg} ({elapsed_ms}ms)"
    else:
        return "error", f"{msg} ({elapsed_ms}ms)"

@router.get("/health/ready")
async def readiness():
    timeout_ms = settings.READINESS_DB_TIMEOUT_MS  # super short, default 300ms
    state, detail = await _maybe_ping_db(settings.DATABASE_URL, timeout_ms)

    payload = {
        "ready": state in ("skipped", "ok"),
        "db": state,
        "detail": detail,
    }

    status_code = status.HTTP_200_OK if payload["ready"] else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response(
        content=__import__("json").dumps(payload),
        media_type="application/json",
        status_code=status_code,
    )
