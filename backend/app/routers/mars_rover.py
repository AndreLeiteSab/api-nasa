"""Mars Rover Photos — Curiosity, Opportunity, Spirit and Perseverance imagery."""

from typing import Any

from fastapi import APIRouter, Path, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/mars-rover", tags=["Mars Rover Photos"])

_BASE = f"{settings.nasa_base_url}/mars-photos/api/v1"


@router.get("/rovers", summary="Listar rovers e seus status")
async def list_rovers() -> Any:
    return await fetch_json(f"{_BASE}/rovers")


@router.get("/rovers/{rover}", summary="Detalhes de um rover")
async def get_rover(
    rover: str = Path(..., description="curiosity, opportunity, spirit ou perseverance."),
) -> Any:
    return await fetch_json(f"{_BASE}/rovers/{rover}")


@router.get("/manifests/{rover}", summary="Manifesto da missão de um rover")
async def get_manifest(
    rover: str = Path(..., description="Nome do rover."),
) -> Any:
    """Mission manifest: total photos, cameras and sols available per rover."""
    return await fetch_json(f"{_BASE}/manifests/{rover}")


@router.get("/rovers/{rover}/photos", summary="Fotos por sol ou data terrestre")
async def get_photos(
    rover: str = Path(..., description="Nome do rover."),
    sol: int | None = Query(None, description="Sol marciano (dia da missão)."),
    earth_date: str | None = Query(None, description="Data terrestre YYYY-MM-DD."),
    camera: str | None = Query(None, description="Abreviação da câmera (ex.: FHAZ, NAVCAM)."),
    page: int | None = Query(None, description="Página (25 fotos por página)."),
) -> Any:
    """Photos taken by a rover, filtered by sol OR earth_date (one is required)."""
    return await fetch_json(
        f"{_BASE}/rovers/{rover}/photos",
        {"sol": sol, "earth_date": earth_date, "camera": camera, "page": page},
    )


@router.get("/rovers/{rover}/latest_photos", summary="Fotos mais recentes do rover")
async def get_latest_photos(
    rover: str = Path(..., description="Nome do rover."),
    camera: str | None = Query(None, description="Abreviação da câmera."),
    page: int | None = Query(None),
) -> Any:
    return await fetch_json(
        f"{_BASE}/rovers/{rover}/latest_photos",
        {"camera": camera, "page": page},
    )
