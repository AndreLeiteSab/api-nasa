"""Application configuration loaded from environment variables.

The settings are read once at import time and reused across the app. We never
store NASA data here — only the credentials and tuning knobs required to talk to
the upstream NASA services.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Values come from environment variables (and the local ``.env`` file during
    development). ``NASA_API_KEY`` falls back to ``DEMO_KEY`` so the project runs
    out of the box, but DEMO_KEY is heavily rate-limited and should be replaced.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # NASA credentials
    nasa_api_key: str = "DEMO_KEY"

    # Upstream base URLs (kept configurable so they can be swapped/mocked)
    nasa_base_url: str = "https://api.nasa.gov"
    eonet_base_url: str = "https://eonet.gsfc.nasa.gov/api/v3"
    images_base_url: str = "https://images-api.nasa.gov"
    exoplanet_base_url: str = (
        "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI"
    )
    tle_base_url: str = "https://tle.ivanstanojevic.me/api"
    ssd_base_url: str = "https://ssd-api.jpl.nasa.gov"

    # HTTP client tuning
    request_timeout: float = 30.0
    max_connections: int = 50

    # CORS — comma separated list of allowed origins for the frontend
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # App metadata
    app_name: str = "NASA API Gateway"
    app_version: str = "1.0.0"

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a clean list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (single source of truth)."""
    return Settings()


settings = get_settings()
