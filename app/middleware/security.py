from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.settings import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to every response.

    CSP is tuned for our current setup:
      - Scripts: from self only
      - Styles: self + 'unsafe-inline' (templates use inline styles)
      - Images/fonts: self + data: (for small embeds)
      - Connect: self (API calls on same origin)
      - No framing

    HSTS is OFF by default and should be enabled only when the app is served over HTTPS.
    """

    def __init__(self, app):
        super().__init__(app)

        # Content Security Policy (dev-friendly, React island safe)
        self.csp_value = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'"
        )

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Core hardening headers
        response.headers["Content-Security-Policy"] = self.csp_value
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # HSTS (only enable when served over HTTPS)
        if settings.ENABLE_HSTS:
            # 1 year, include subdomains, signal preload intent
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response
