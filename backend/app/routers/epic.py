"""EPIC — Earth Polychromatic Imaging Camera (imagens da Terra inteira).

A API EPIC da NASA retorna apenas os *metadados* das imagens (uma lista JSON por
data); as fotos em si ficam em um arquivo separado, organizado por data, cuja URL
precisa ser montada a partir dos campos ``date`` e ``image`` de cada registro e
assinada com a ``api_key``. Para manter essa chave no servidor (e o frontend
falando só com este gateway), expomos uma rota de *proxy* de imagem e enriquecemos
cada resposta de metadados com links ``image_url`` prontos apontando para ela.
"""

from typing import Any

from fastapi import APIRouter, Path, Query, Request, Response

from app.config import settings
from app.core.nasa_client import fetch_bytes, fetch_json

router = APIRouter(prefix="/epic", tags=["EPIC - Imagens da Terra (DSCOVR)"])

_BASE = f"{settings.nasa_base_url}/EPIC/api"
_ARCHIVE = f"{settings.nasa_base_url}/EPIC/archive"

_COLLECTIONS = {"natural", "enhanced"}


def _validate_collection(collection: str) -> str:
    if collection not in _COLLECTIONS:
        # assume natural em vez de repassar um caminho inválido para a NASA
        return "natural"
    return collection


def _split_date(date: str) -> tuple[str, str, str]:
    """retorna (ano, mês, dia) a partir de uma string de data

    Os metadados do EPIC trazem ``date`` como ``"YYYY-MM-DD HH:MM:SS"``, mas quem
    chama também pode passar só ``"YYYY-MM-DD"``. Só interessa a parte do dia,
    então pegamos os 10 primeiros caracteres antes de separar.
    """
    year, month, day = date[:10].split("-")
    return year, month, day


def _archive_url(collection: str, date: str, image: str, fmt: str) -> str:
    """monta a URL assinada do arquivo da NASA para uma única imagem EPIC"""
    year, month, day = _split_date(date)
    ext = "jpg" if fmt == "thumbs" else fmt
    return (
        f"{_ARCHIVE}/{collection}/{year}/{month}/{day}/{fmt}/{image}.{ext}"
        f"?api_key={settings.nasa_api_key}"
    )


def _with_image_urls(request: Request, collection: str, data: Any) -> Any:
    """injeta links de imagem relativos ao gateway em cada registro do EPIC

    ``image_url`` aponta para o thumbnail leve (galerias rápidas) e
    ``image_url_hd`` para o PNG em resolução cheia. Ambos passam pelo proxy de
    imagem deste gateway, então a ``api_key`` da NASA nunca é exposta ao
    navegador. No resto, a resposta da NASA é repassada sem alterações.
    """
    if not isinstance(data, list):
        return data
    for record in data:
        if not isinstance(record, dict):
            continue
        image, date = record.get("image"), record.get("date")
        if not (isinstance(image, str) and isinstance(date, str)):
            continue
        day = date[:10]
        base = request.url_for(
            "epic_image", collection=collection, date=day, image=image
        ).path
        record["image_url"] = f"{base}?fmt=thumbs"
        record["image_url_hd"] = base
    return data


@router.get("/{collection}", summary="Metadados das imagens mais recentes")
async def get_latest(
    request: Request,
    collection: str = Path(..., description="natural ou enhanced."),
) -> Any:
    """metadados das imagens EPIC mais recentes da coleção escolhida"""
    coll = _validate_collection(collection)
    data = await fetch_json(f"{_BASE}/{coll}")
    return _with_image_urls(request, coll, data)


@router.get("/{collection}/date/{date}", summary="Imagens de uma data específica")
async def get_by_date(
    request: Request,
    collection: str = Path(..., description="natural ou enhanced."),
    date: str = Path(..., description="Data YYYY-MM-DD."),
) -> Any:
    coll = _validate_collection(collection)
    data = await fetch_json(f"{_BASE}/{coll}/date/{date}")
    return _with_image_urls(request, coll, data)


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


@router.get(
    "/{collection}/image/{date}/{image}",
    summary="Imagem EPIC (proxy do arquivo da NASA)",
    response_class=Response,
    name="epic_image",
)
async def epic_image(
    collection: str = Path(..., description="natural ou enhanced."),
    date: str = Path(..., description="Data YYYY-MM-DD."),
    image: str = Path(..., description="Nome do arquivo (campo 'image' dos metadados)."),
    fmt: str = Query("png", description="Formato: png, jpg ou thumbs."),
) -> Response:
    """faz o streaming de uma imagem do arquivo EPIC, mantendo a ``api_key`` no servidor

    O frontend renderiza tags ``<img>`` apontando para cá; buscamos a foto no
    arquivo da NASA e repassamos os bytes brutos, então o gateway continua sendo
    apenas um repassador.
    """
    coll = _validate_collection(collection)
    content, content_type = await fetch_bytes(
        _archive_url(coll, date, image, fmt), with_api_key=False
    )
    return Response(content=content, media_type=content_type)


@router.get("/{collection}/image-url", summary="Montar URL da imagem EPIC")
async def build_image_url(
    collection: str = Path(..., description="natural ou enhanced."),
    date: str = Query(..., description="Data da imagem YYYY-MM-DD."),
    image: str = Query(..., description="Nome do arquivo (campo 'image' dos metadados)."),
    fmt: str = Query("png", description="Formato: png, jpg ou thumbs."),
) -> dict[str, str]:
    """auxiliar que monta a URL de arquivo de uma imagem EPIC

    As imagens EPIC são servidas a partir de um caminho de arquivo organizado por
    data. Este endpoint de conveniência monta essa URL (incluindo a api_key) para
    o frontend não precisar conhecer a estrutura do arquivo.
    """
    coll = _validate_collection(collection)
    return {"image_url": _archive_url(coll, date, image, fmt)}
