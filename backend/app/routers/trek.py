"""Vesta / Moon / Mars Trek — imagens WMTS e busca por índice (sem API key).

Cada corpo do Trek oferece um índice JSON ``searchItems``, além de tiles de mapa
WMTS e um documento XML ``GetCapabilities``. Repassamos um exemplo de cada
interação GET para os três corpos suportados.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Path, Query, Response

from app.config import settings
from app.core.nasa_client import fetch_bytes, fetch_json, fetch_text

router = APIRouter(prefix="/trek", tags=["Trek WMTS - Vesta/Moon/Mars"])

_BASE = settings.trek_base_url

# cada corpo mapeia para o caminho de tiles capitalizado e um mosaico global padrão
_BODIES: dict[str, dict[str, str]] = {
    "moon": {"path": "Moon", "product": "LRO_WAC_Mosaic_Global_303ppd_v02"},
    "mars": {"path": "Mars", "product": "Mars_Viking_MDIM21_ClrMosaic_global_232m"},
    "vesta": {"path": "Vesta", "product": "Vesta_Dawn_FC_HAMO_Mosaic_Global_74ppd"},
}


def _resolve(body: str) -> dict[str, str]:
    info = _BODIES.get(body.lower())
    if info is None:
        raise HTTPException(
            status_code=404,
            detail=f"Corpo inválido '{body}'. Use: {', '.join(_BODIES)}.",
        )
    return info


@router.get("/{body}/search", summary="Buscar itens indexados (nomenclatura, produtos...)")
async def search(
    body: str = Path(..., description="moon, mars ou vesta."),
    start: int | None = Query(None, description="Deslocamento (paginação)."),
    rows: int | None = Query(None, description="Quantidade de itens."),
) -> Any:
    """repassa o endpoint de índice ``searchItems`` do Trek para o corpo informado"""
    body = body.lower()
    _resolve(body)
    return await fetch_json(
        f"{_BASE}/{body}/TrekServices/ws/index/eq/searchItems",
        {"start": start, "rows": rows},
        with_api_key=False,
    )


@router.get(
    "/{body}/capabilities",
    summary="Catálogo WMTS do mosaico global (GetCapabilities, XML)",
    response_class=Response,
)
async def capabilities(
    body: str = Path(..., description="moon, mars ou vesta."),
    product: str | None = Query(None, description="Produto WMTS (padrão: mosaico global)."),
) -> Response:
    """repassa o XML ``GetCapabilities`` (WMTS) do mosaico global de um corpo"""
    info = _resolve(body)
    layer = product or info["product"]
    text, content_type = await fetch_text(
        f"{_BASE}/tiles/{info['path']}/EQ/{layer}/1.0.0/WMTSCapabilities.xml",
    )
    return Response(content=text, media_type=content_type)


@router.get(
    "/{body}/tile/{tile_matrix}/{tile_row}/{tile_col}",
    summary="Tile do mosaico global (imagem)",
    response_class=Response,
)
async def tile(
    body: str = Path(..., description="moon, mars ou vesta."),
    tile_matrix: int = Path(..., description="Nível de zoom (0 = global)."),
    tile_row: int = Path(..., description="Linha do tile."),
    tile_col: int = Path(..., description="Coluna do tile."),
    product: str | None = Query(None, description="Produto WMTS (padrão: mosaico global)."),
) -> Response:
    """retorna um único tile de mapa WMTS (imagem binária) do mosaico do corpo"""
    info = _resolve(body)
    layer = product or info["product"]
    url = (
        f"{_BASE}/tiles/{info['path']}/EQ/{layer}/1.0.0/"
        f"default/default028mm/{tile_matrix}/{tile_row}/{tile_col}.jpg"
    )
    content, content_type = await fetch_bytes(url, with_api_key=False)
    return Response(content=content, media_type=content_type)
