"""Earth — Landsat 8 imagery and asset metadata for a lat/lon point."""

from typing import Any

from fastapi import APIRouter, Query, Response

from app.config import settings
from app.core.nasa_client import fetch_bytes, fetch_json

router = APIRouter(prefix="/earth", tags=["Earth - Imagens de satélite"])

_BASE = f"{settings.nasa_base_url}/planetary/earth"


@router.get(
    "/imagery",
    summary="Imagem de satélite (PNG) de um ponto",
    response_class=Response,
)
async def get_imagery(
    lat: float = Query(..., description="Latitude."),
    lon: float = Query(..., description="Longitude."),
    dim: float | None = Query(None, description="Largura/altura em graus (default 0.025)."),
    date: str | None = Query(None, description="Data YYYY-MM-DD (imagem mais próxima)."),
) -> Response:
    """Return a Landsat 8 image (PNG bytes) for the given coordinates."""
    content, content_type = await fetch_bytes(
        f"{_BASE}/imagery",
        {"lat": lat, "lon": lon, "dim": dim, "date": date},
    )
    return Response(content=content, media_type=content_type)


@router.get("/assets", summary="Metadados de imagens disponíveis para um ponto")
async def get_assets(
    lat: float = Query(..., description="Latitude."),
    lon: float = Query(..., description="Longitude."),
    date: str | None = Query(None, description="Data inicial YYYY-MM-DD."),
    dim: float | None = Query(None, description="Largura/altura em graus."),
) -> Any:
    """Return metadata (dates/ids) of available imagery for the coordinates."""
    return await fetch_json(
        f"{_BASE}/assets",
        {"lat": lat, "lon": lon, "date": date, "dim": dim},
    )
