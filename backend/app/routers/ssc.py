"""Satellite Situation Center (SSC) — serviço de localização geocêntrica de naves.

O serviço REST do SSCWeb retorna XML por padrão; pedimos JSON pelo cabeçalho
``Accept``. Não exige API key. Expomos os endpoints de catálogo somente leitura
(naves/observatórios e estações terrestres).
"""

from typing import Any

from fastapi import APIRouter

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/ssc", tags=["Satellite Situation Center"])

_BASE = settings.ssc_base_url
# o SSCWeb negocia o tipo de conteúdo via Accept; sem isso ele responde XML
_JSON_HEADERS = {"Accept": "application/json"}


@router.get("/observatories", summary="Naves/observatórios disponíveis no SSC")
async def observatories() -> Any:
    """lista todas as naves/observatórios rastreados pelo SSCWeb"""
    return await fetch_json(
        f"{_BASE}/observatories", with_api_key=False, headers=_JSON_HEADERS
    )


@router.get("/ground-stations", summary="Estações terrestres registradas")
async def ground_stations() -> Any:
    """lista as estações terrestres conhecidas pelo SSCWeb"""
    return await fetch_json(
        f"{_BASE}/groundStations", with_api_key=False, headers=_JSON_HEADERS
    )
