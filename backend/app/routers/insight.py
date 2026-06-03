"""InSight — Mars Weather Service (legacy; data may be empty as the mission ended)."""

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
    """Latest available Martian weather from the InSight lander."""
    return await fetch_json(_URL, {"ver": ver, "feedtype": feedtype})
