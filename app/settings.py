from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict
from app.__version__ import VERSION as APP_VERSION

class Settings(BaseSettings):
    # App identity
    APP_NAME: str = "FastAPI Blog"
    APP_ENV: str = "development"  # development | staging | production

    # DB (not exposed in public config)
    DATABASE_URL: Optional[str] = None

    # Feature flags (runtime-togglable, safe to expose)
    ENABLE_DEMO_BANNER: bool = False
    ENABLE_EXPERIMENTAL_UI: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def public_dict(self) -> Dict:
        """
        Return a safe subset for clients. Never include secrets or connection strings.
        """
        return {
            "name": self.APP_NAME,
            "env": self.APP_ENV,
            "version": APP_VERSION,  # Hard-coded constant
            "features": {
                "demoBanner": self.ENABLE_DEMO_BANNER,
                "experimentalUI": self.ENABLE_EXPERIMENTAL_UI,
            },
            "staticBase": "/static",
        }

settings = Settings()
