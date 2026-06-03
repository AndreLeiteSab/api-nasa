"""EONET — Earth Observatory Natural Event Tracker.

EONET lives on its own host and does NOT require an API key.
"""

from typing import Any

from fastapi import APIRouter, Path, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/eonet", tags=["EONET - Eventos naturais da Terra"])

_BASE = settings.eonet_base_url


@router.get("/events", summary="Eventos naturais (incêndios, tempestades, etc.)")
async def get_events(
    source: str | None = Query(None, description="Filtrar por fonte (ex.: InciWeb)."),
    status: str | None = Query(None, description="open ou closed."),
    limit: int | None = Query(None, description="Número máximo de eventos."),
    days: int | None = Query(None, description="Eventos dos últimos N dias."),
    category: str | None = Query(None, description="ID/nome da categoria."),
    start: str | None = Query(None, description="Data inicial YYYY-MM-DD."),
    end: str | None = Query(None, description="Data final YYYY-MM-DD."),
    mag_id: str | None = Query(None, alias="magID", description="ID de magnitude."),
    mag_min: float | None = Query(None, alias="magMin"),
    mag_max: float | None = Query(None, alias="magMax"),
    bbox: str | None = Query(None, description="Caixa delimitadora geográfica."),
) -> Any:
    """List natural events tracked by EONET."""
    return await fetch_json(
        f"{_BASE}/events",
        {
            "source": source,
            "status": status,
            "limit": limit,
            "days": days,
            "category": category,
            "start": start,
            "end": end,
            "magID": mag_id,
            "magMin": mag_min,
            "magMax": mag_max,
            "bbox": bbox,
        },
        with_api_key=False,
    )


@router.get("/categories", summary="Listar categorias de eventos")
async def get_categories() -> Any:
    return await fetch_json(f"{_BASE}/categories", with_api_key=False)


@router.get("/categories/{category_id}", summary="Eventos de uma categoria")
async def get_category(
    category_id: str = Path(..., description="ID da categoria."),
    status: str | None = Query(None),
    limit: int | None = Query(None),
    days: int | None = Query(None),
) -> Any:
    return await fetch_json(
        f"{_BASE}/categories/{category_id}",
        {"status": status, "limit": limit, "days": days},
        with_api_key=False,
    )


@router.get("/layers", summary="Camadas (web service layers)")
async def get_layers() -> Any:
    return await fetch_json(f"{_BASE}/layers", with_api_key=False)


@router.get("/sources", summary="Fontes de dados de eventos")
async def get_sources() -> Any:
    return await fetch_json(f"{_BASE}/sources", with_api_key=False)


@router.get("/magnitudes", summary="Tipos de magnitude disponíveis")
async def get_magnitudes() -> Any:
    return await fetch_json(f"{_BASE}/magnitudes", with_api_key=False)
