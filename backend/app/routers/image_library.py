"""NASA Image and Video Library (images-api.nasa.gov) — no API key required."""

from typing import Any

from fastapi import APIRouter, Path, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/images", tags=["Image and Video Library"])

_BASE = settings.images_base_url


@router.get("/search", summary="Buscar imagens, vídeos e áudios")
async def search(
    q: str | None = Query(None, description="Termo livre de busca."),
    center: str | None = Query(None, description="Centro da NASA."),
    description: str | None = Query(None),
    keywords: str | None = Query(None, description="Palavras-chave separadas por vírgula."),
    location: str | None = Query(None),
    media_type: str | None = Query(None, description="image, video ou audio."),
    nasa_id: str | None = Query(None),
    page: int | None = Query(None),
    page_size: int | None = Query(None, le=100),
    photographer: str | None = Query(None),
    title: str | None = Query(None),
    year_start: str | None = Query(None, description="Ano inicial (YYYY)."),
    year_end: str | None = Query(None, description="Ano final (YYYY)."),
) -> Any:
    """Full-text search across the NASA media library."""
    return await fetch_json(
        f"{_BASE}/search",
        {
            "q": q,
            "center": center,
            "description": description,
            "keywords": keywords,
            "location": location,
            "media_type": media_type,
            "nasa_id": nasa_id,
            "page": page,
            "page_size": page_size,
            "photographer": photographer,
            "title": title,
            "year_start": year_start,
            "year_end": year_end,
        },
        with_api_key=False,
    )


@router.get("/asset/{nasa_id}", summary="Arquivos de mídia de um item")
async def get_asset(nasa_id: str = Path(..., description="ID NASA do item.")) -> Any:
    return await fetch_json(f"{_BASE}/asset/{nasa_id}", with_api_key=False)


@router.get("/metadata/{nasa_id}", summary="Local dos metadados de um item")
async def get_metadata(nasa_id: str = Path(...)) -> Any:
    return await fetch_json(f"{_BASE}/metadata/{nasa_id}", with_api_key=False)


@router.get("/captions/{nasa_id}", summary="Legendas de um vídeo")
async def get_captions(nasa_id: str = Path(...)) -> Any:
    return await fetch_json(f"{_BASE}/captions/{nasa_id}", with_api_key=False)


@router.get("/album/{album_name}", summary="Conteúdo de um álbum")
async def get_album(
    album_name: str = Path(...),
    page: int | None = Query(None),
    page_size: int | None = Query(None),
) -> Any:
    return await fetch_json(
        f"{_BASE}/album/{album_name}",
        {"page": page, "page_size": page_size},
        with_api_key=False,
    )
