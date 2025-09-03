import logging
import time
import uuid
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging_config import request_id_ctx

_log = logging.getLogger("app")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Generates/propagates a request ID, adds it to responses (X-Request-ID),
    and emits a structured JSON line per request with method/path/status/duration.
    """

    def _get_incoming_id(self, request: Request) -> Optional[str]:
        return (
            request.headers.get("x-request-id")
            or request.headers.get("x-correlation-id")
            or None
        )

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        rid = self._get_incoming_id(request) or str(uuid.uuid4())
        token = request_id_ctx.set(rid)
        request.state.request_id = rid  # handy if handlers want it

        response: Response
        try:
            response = await call_next(request)
            duration_ms = int((time.perf_counter() - start) * 1000)

            # Log while the context is still set; also pass request_id explicitly
            _log.info(
                "HTTP request",
                extra={
                    "event": "http_request",
                    "request_id": rid,
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query) if request.url.query else "",
                    "status": getattr(response, "status_code", 0),
                    "duration_ms": duration_ms,
                    "client": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                },
            )
        finally:
            # Add header and then clear context
            # (header assignment after call_next still applies before send)
            # NOTE: if an exception bubbles, Starlette still attempts to send a response;
            # X-Request-ID may not be present in some fatal cases.
            if "X-Request-ID" not in getattr(response, "headers", {}):
                try:
                    response.headers["X-Request-ID"] = rid
                except Exception:
                    pass
            request_id_ctx.reset(token)

        return response
