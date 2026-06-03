"""NeoWs — Near Earth Object Web Service (asteroids)."""

from typing import Any

from fastapi import APIRouter, Path, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/neows", tags=["NeoWs - Asteroides (Near Earth Objects)"])

_BASE = f"{settings.nasa_base_url}/neo/rest/v1"


@router.get("/feed", summary="Asteroides por intervalo de datas")
async def get_feed(
    start_date: str | None = Query(None, description="Início (YYYY-MM-DD)."),
    end_date: str | None = Query(None, description="Fim (YYYY-MM-DD, máx. 7 dias após o início)."),
    detailed: bool | None = Query(None, description="Incluir dados orbitais detalhados."),
) -> Any:
    """List near-earth asteroids approaching within the given date range."""
    return await fetch_json(
        f"{_BASE}/feed",
        {"start_date": start_date, "end_date": end_date, "detailed": detailed},
    )


@router.get("/browse", summary="Listar/paginar todos os asteroides")
async def browse(
    page: int | None = Query(None, ge=0, description="Número da página."),
    size: int | None = Query(None, ge=1, le=100, description="Itens por página."),
) -> Any:
    """Browse the overall asteroid dataset (paginated)."""
    return await fetch_json(f"{_BASE}/neo/browse", {"page": page, "size": size})


@router.get("/{asteroid_id}", summary="Detalhes de um asteroide por ID")
async def lookup(
    asteroid_id: str = Path(..., description="SPK-ID do asteroide."),
) -> Any:
    """Look up a single asteroid by its NASA JPL SPK-ID."""
    return await fetch_json(f"{_BASE}/neo/{asteroid_id}")
