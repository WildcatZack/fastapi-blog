from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict

class Settings(BaseSettings):
    # App identity
    APP_NAME: str = "FastAPI Blog"
    APP_ENV: str = "development"  # development | staging | production
    APP_VERSION: str = "0.2.0"    # bump as we go

    # DB: users can set env; we won't expose this in /api/config
    DATABASE_URL: Optional[str] = None

    # Feature flags (example flags you can flip at runtime)
    ENABLE_DEMO_BANNER: bool = False
    ENABLE_EXPERIMENTAL_UI: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def public_dict(self) -> Dict[str, str]:
        """
        Safe subset for clients. Do NOT include secrets or connection strings.
        """
        return {
            "name": self.APP_NAME,
            "env": self.APP_ENV,
            "version": self.APP_VERSION,
            "features": {
                "demoBanner": self.ENABLE_DEMO_BANNER,
                "experimentalUI": self.ENABLE_EXPERIMENTAL_UI,
            },
            # static base path for assets; adjust later if you add CDN
            "staticBase": "/static",
        }

settings = Settings()
