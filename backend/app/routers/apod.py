"""APOD — Imagem Astronômica do Dia (Astronomy Picture of the Day)."""

from typing import Any

from fastapi import APIRouter, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/apod", tags=["APOD - Astronomy Picture of the Day"])

_URL = f"{settings.nasa_base_url}/planetary/apod"


@router.get("", summary="Imagem astronômica do dia")
async def get_apod(
    date: str | None = Query(None, description="Data YYYY-MM-DD da imagem desejada."),
    start_date: str | None = Query(None, description="Início do intervalo (YYYY-MM-DD)."),
    end_date: str | None = Query(None, description="Fim do intervalo (YYYY-MM-DD)."),
    count: int | None = Query(None, description="Quantidade de imagens aleatórias."),
    thumbs: bool | None = Query(None, description="Retornar thumbnail de vídeos."),
) -> Any:
    """retorna a imagem astronômica do dia (ou um intervalo / conjunto aleatório)"""
    return await fetch_json(
        _URL,
        {
            "date": date,
            "start_date": start_date,
            "end_date": end_date,
            "count": count,
            "thumbs": thumbs,
        },
    )
