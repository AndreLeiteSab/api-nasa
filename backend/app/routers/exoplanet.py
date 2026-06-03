"""Exoplanet Archive — query exoplanet datasets (no NASA api.nasa.gov key)."""

from typing import Any

from fastapi import APIRouter, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/exoplanet", tags=["Exoplanet Archive"])

_URL = settings.exoplanet_base_url


@router.get("", summary="Consultar arquivo de exoplanetas")
async def query_exoplanets(
    table: str = Query("exoplanets", description="Tabela (ex.: exoplanets, cumulative)."),
    select: str | None = Query(None, description="Colunas a retornar."),
    where: str | None = Query(None, description="Cláusula WHERE (filtro SQL-like)."),
    order: str | None = Query(None, description="Ordenação."),
    format: str = Query("json", description="Formato de saída (json, csv, ...)."),
) -> Any:
    """Proxy to the NASA Exoplanet Archive query service."""
    return await fetch_json(
        _URL,
        {
            "table": table,
            "select": select,
            "where": where,
            "order": order,
            "format": format,
        },
        with_api_key=False,
    )
