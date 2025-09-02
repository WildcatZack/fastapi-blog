from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, List
from app.__version__ import VERSION as APP_VERSION

def _split_csv(value: str) -> List[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]

class Settings(BaseSettings):
    # App identity
    APP_NAME: str = "FastAPI Blog"
    APP_ENV: str = "development"  # development | staging | production

    # DB (not exposed in public config)
    DATABASE_URL: Optional[str] = None

    # Feature flags (runtime-togglable, safe to expose)
    ENABLE_DEMO_BANNER: bool = False
    ENABLE_EXPERIMENTAL_UI: bool = False

    # Security toggles (NOT exposed)
    ENABLE_HSTS: bool = False  # enable only when behind HTTPS (NPM)

    # Readiness probe tuning (milliseconds)
    READINESS_DB_TIMEOUT_MS: int = 300

    # ---- CORS (disabled by default) ----
    # Comma-separated list of origins (e.g. "http://localhost:5173,https://example.com")
    CORS_ALLOW_ORIGINS: str = ""         # empty = disabled; "*" = any
    # Comma-separated methods and headers
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    CORS_ALLOW_HEADERS: str = "Authorization,Content-Type"
    # Credentials require explicit origins (not "*")
    CORS_ALLOW_CREDENTIALS: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Safe subset for clients
    def public_dict(self) -> Dict:
        return {
            "name": self.APP_NAME,
            "env": self.APP_ENV,
            "version": APP_VERSION,
            "features": {
                "demoBanner": self.ENABLE_DEMO_BANNER,
                "experimentalUI": self.ENABLE_EXPERIMENTAL_UI,
            },
            "staticBase": "/static",
        }

    # Parsed CORS config for app startup
    @property
    def cors_origins(self) -> List[str]:
        return _split_csv(self.CORS_ALLOW_ORIGINS)

    @property
    def cors_methods(self) -> List[str]:
        vals = [m.upper() for m in _split_csv(self.CORS_ALLOW_METHODS)]
        return vals or ["GET", "POST", "OPTIONS"]

    @property
    def cors_headers(self) -> List[str]:
        vals = _split_csv(self.CORS_ALLOW_HEADERS)
        return vals or ["Authorization", "Content-Type"]

settings = Settings()
