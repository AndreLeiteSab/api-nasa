"""GIBS — Global Imagery Browse Services (imagens de satélite WMTS, sem API key).

O GIBS não expõe uma API REST JSON; ele serve tiles de mapa pré-renderizados via
WMTS. Repassamos as duas interações GET que importam para um cliente:

* ``GetCapabilities`` — o catálogo XML que descreve cada camada disponível.
* um único tile de mapa (imagem binária) para uma camada/data/zoom/linha/coluna.

``/gibs/layers`` é um pequeno descritor curado (metadados nossos, não dados da
NASA) para o frontend ter exemplos prontos para usar o endpoint de tiles.
"""

from fastapi import APIRouter, Path, Query, Response

from app.config import settings
from app.core.nasa_client import fetch_bytes, fetch_text

router = APIRouter(prefix="/gibs", tags=["GIBS - Imagens de satélite (WMTS)"])

_BASE = settings.gibs_base_url

# exemplos curados para a UI exibir tiles sem precisar ler o documento de
# capabilities de 5 MB. é configuração descritiva, não dado armazenado da NASA
_LAYERS = [
    {
        "id": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "title": "MODIS Terra — True Color",
        "format": "jpg",
        "tile_matrix_set": "250m",
        "example": {"date": "2024-01-01", "tile_matrix": 2, "tile_row": 1, "tile_col": 2},
    },
    {
        "id": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
        "title": "VIIRS SNPP — True Color",
        "format": "jpg",
        "tile_matrix_set": "250m",
        "example": {"date": "2024-01-01", "tile_matrix": 2, "tile_row": 1, "tile_col": 2},
    },
    {
        "id": "BlueMarble_NextGeneration",
        "title": "Blue Marble (Next Generation)",
        "format": "jpg",
        "tile_matrix_set": "500m",
        "example": {"date": "2004-08-01", "tile_matrix": 2, "tile_row": 1, "tile_col": 2},
    },
]


@router.get("/layers", summary="Camadas GIBS disponíveis (exemplos prontos)")
async def layers() -> dict:
    """retorna uma lista curada de camadas populares do GIBS e coordenadas de tile de exemplo"""
    return {"epsg": "epsg4326", "layers": _LAYERS}


@router.get("/capabilities", summary="Catálogo WMTS (GetCapabilities, XML)", response_class=Response)
async def capabilities(
    epsg: str = Query("epsg4326", description="Projeção (epsg4326, epsg3857, epsg3413, epsg3031)."),
) -> Response:
    """repassa o documento XML ``GetCapabilities`` (WMTS) da projeção informada"""
    text, content_type = await fetch_text(
        f"{_BASE}/{epsg}/best/1.0.0/WMTSCapabilities.xml",
    )
    return Response(content=text, media_type=content_type)


@router.get(
    "/tile/{tile_matrix}/{tile_row}/{tile_col}",
    summary="Tile de mapa (imagem) de uma camada",
    response_class=Response,
)
async def tile(
    tile_matrix: int = Path(..., description="Nível de zoom (TileMatrix)."),
    tile_row: int = Path(..., description="Linha do tile (TileRow)."),
    tile_col: int = Path(..., description="Coluna do tile (TileCol)."),
    layer: str = Query(
        "MODIS_Terra_CorrectedReflectance_TrueColor", description="Identificador da camada."
    ),
    date: str = Query("2024-01-01", description="Data da imagem (YYYY-MM-DD)."),
    tile_matrix_set: str = Query("250m", description="Conjunto de matrizes (ex.: 250m, 500m)."),
    format: str = Query("jpg", description="Formato do tile (jpg ou png)."),
    epsg: str = Query("epsg4326", description="Projeção."),
) -> Response:
    """retorna um único tile de mapa WMTS (imagem binária) da camada solicitada"""
    url = (
        f"{_BASE}/{epsg}/best/{layer}/default/{date}/"
        f"{tile_matrix_set}/{tile_matrix}/{tile_row}/{tile_col}.{format}"
    )
    content, content_type = await fetch_bytes(url, with_api_key=False)
    return Response(content=content, media_type=content_type)
