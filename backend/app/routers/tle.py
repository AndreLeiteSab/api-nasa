"""TLE — conjuntos Two-Line Element de satélites em órbita da Terra (sem API key)."""

from typing import Any

from fastapi import APIRouter, Path, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/tle", tags=["TLE - Órbitas de satélites"])

_BASE = settings.tle_base_url


@router.get("", summary="Buscar/paginar conjuntos TLE")
async def search(
    search: str | None = Query(None, description="Nome do satélite."),
    page: int | None = Query(None),
    page_size: int | None = Query(None, alias="page-size"),
) -> Any:
    return await fetch_json(
        f"{_BASE}/tle",
        {"search": search, "page": page, "page-size": page_size},
        with_api_key=False,
    )


@router.get("/{satellite_number}", summary="TLE de um satélite por NORAD ID")
async def get_one(
    satellite_number: int = Path(..., description="Número de catálogo NORAD."),
) -> Any:
    return await fetch_json(f"{_BASE}/tle/{satellite_number}", with_api_key=False)
