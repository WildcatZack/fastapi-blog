import json
import logging
import logging.config
import time
from typing import Any, Dict, Optional
from app.settings import settings

from contextvars import ContextVar
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Injects request_id from contextvar into each LogRecord, unless already set."""
    def filter(self, record: logging.LogRecord) -> bool:
        # Prefer an explicit record.request_id (from logger extra) over contextvar
        current = getattr(record, "request_id", None)
        if current is None:
            setattr(record, "request_id", request_id_ctx.get())
        # Always attach env
        setattr(record, "app_env", getattr(settings, "APP_ENV", "unknown"))
        return True


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter for Docker logs."""
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "env": getattr(record, "app_env", None),
        }
        for k in ("method", "path", "query", "status", "duration_ms", "client", "user_agent", "event"):
            if hasattr(record, k):
                payload[k] = getattr(record, k)
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def setup_logging() -> None:
    """Configure root/app/uvicorn loggers to output JSON with request_id."""
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {"()": RequestIdFilter},
        },
        "formatters": {
            "json": {"()": JsonFormatter},
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "filters": ["request_id"],
                "formatter": "json",
            }
        },
        "loggers": {
            "app": {
                "handlers": ["default"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["default"],
            "level": settings.LOG_LEVEL,
        },
    }
    logging.config.dictConfig(config)
