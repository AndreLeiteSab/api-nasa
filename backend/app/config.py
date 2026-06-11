"""Configuração da aplicação carregada a partir de variáveis de ambiente.

As configurações são lidas uma única vez na importação e reaproveitadas em toda
a aplicação. Nunca armazenamos dados da NASA aqui — apenas as credenciais e os
ajustes necessários para conversar com os serviços da NASA.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação com tipos bem definidos.

    Os valores vêm das variáveis de ambiente (e do arquivo ``.env`` local durante
    o desenvolvimento). ``NASA_API_KEY`` assume ``DEMO_KEY`` por padrão para o
    projeto rodar de imediato, mas a DEMO_KEY tem limite de uso baixo (rate limit)
    e deve ser substituída.
    """

    # lê as variáveis de ambiente do arquivo .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # chave api nasa
    nasa_api_key: str = "DEMO_KEY"

    # URLs base para os serviços da NASA (usados pelos routers para construir as requisições)
    nasa_base_url: str = "https://api.nasa.gov"
    eonet_base_url: str = "https://eonet.gsfc.nasa.gov/api/v3"
    images_base_url: str = "https://images-api.nasa.gov"
    # exoplanetarchive tem uma API TAP (Table Access Protocol) que é um pouco diferente das APIs REST tradicionais, então deixei a URL
    exoplanet_base_url: str = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    tle_base_url: str = "https://tle.ivanstanojevic.me/api"
    ssd_base_url: str = "https://ssd-api.jpl.nasa.gov"
    gibs_base_url: str = "https://gibs.earthdata.nasa.gov/wmts"
    osdr_base_url: str = "https://osdr.nasa.gov/osdr/data"
    ssc_base_url: str = "https://sscweb.gsfc.nasa.gov/WS/sscr/2"
    techport_base_url: str = "https://api.nasa.gov/techport/api"
    trek_base_url: str = "https://trek.nasa.gov"

    # configurações de timeout e conexões para o cliente HTTP
    request_timeout: float = 30.0
    max_connections: int = 50

    # CORS - lista as origens permitidas para o frontend
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    app_name: str = "NASA API Gateway"
    app_version: str = "1.0.0"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
