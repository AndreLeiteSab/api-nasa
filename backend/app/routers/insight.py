"""InSight — serviço de clima de Marte (legado; pode vir vazio, pois a missão acabou)."""

from typing import Any

from fastapi import APIRouter, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/insight", tags=["InSight - Clima em Marte"])

_URL = f"{settings.nasa_base_url}/insight_weather/"


@router.get("", summary="Clima em Marte (InSight)")
async def get_weather(
    ver: str = Query("1.0", description="Versão da API."),
    feedtype: str = Query("json", description="Formato do feed."),
) -> Any:
    """clima marciano mais recente disponível do módulo InSight"""
    return await fetch_json(_URL, {"ver": ver, "feedtype": feedtype})
