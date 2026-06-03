"""EPIC — Earth Polychromatic Imaging Camera (full-disk Earth images)."""

from typing import Any

from fastapi import APIRouter, Path, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/epic", tags=["EPIC - Imagens da Terra (DSCOVR)"])

_BASE = f"{settings.nasa_base_url}/EPIC/api"
_ARCHIVE = f"{settings.nasa_base_url}/EPIC/archive"

_COLLECTIONS = {"natural", "enhanced"}


def _validate_collection(collection: str) -> str:
    if collection not in _COLLECTIONS:
        # Default to natural rather than forwarding an invalid path upstream.
        return "natural"
    return collection


@router.get("/{collection}", summary="Metadados das imagens mais recentes")
async def get_latest(
    collection: str = Path(..., description="natural ou enhanced."),
) -> Any:
    """Most recent EPIC imagery metadata for the chosen collection."""
    return await fetch_json(f"{_BASE}/{_validate_collection(collection)}")


@router.get("/{collection}/date/{date}", summary="Imagens de uma data específica")
async def get_by_date(
    collection: str = Path(..., description="natural ou enhanced."),
    date: str = Path(..., description="Data YYYY-MM-DD."),
) -> Any:
    return await fetch_json(f"{_BASE}/{_validate_collection(collection)}/date/{date}")


@router.get("/{collection}/all", summary="Todas as datas com imagens")
async def get_all_dates(
    collection: str = Path(..., description="natural ou enhanced."),
) -> Any:
    return await fetch_json(f"{_BASE}/{_validate_collection(collection)}/all")


@router.get("/{collection}/available", summary="Datas disponíveis (lista simples)")
async def get_available(
    collection: str = Path(..., description="natural ou enhanced."),
) -> Any:
    return await fetch_json(f"{_BASE}/{_validate_collection(collection)}/available")


@router.get("/{collection}/image-url", summary="Montar URL da imagem EPIC")
async def build_image_url(
    collection: str = Path(..., description="natural ou enhanced."),
    date: str = Query(..., description="Data da imagem YYYY-MM-DD."),
    image: str = Query(..., description="Nome do arquivo (campo 'image' dos metadados)."),
    fmt: str = Query("png", description="Formato: png, jpg ou thumbs."),
) -> dict[str, str]:
    """Helper that builds the archive URL for an EPIC image.

    EPIC images are served from a date-based archive path. This convenience
    endpoint assembles that URL (including the api_key) so the frontend doesn't
    have to know the archive layout.
    """
    coll = _validate_collection(collection)
    year, month, day = date.split("-")
    url = (
        f"{_ARCHIVE}/{coll}/{year}/{month}/{day}/{fmt}/{image}.{('jpg' if fmt == 'thumbs' else fmt)}"
        f"?api_key={settings.nasa_api_key}"
    )
    return {"image_url": url}
