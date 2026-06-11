"""Open Science Data Repository (OSDR / GeneLab) — datasets de biologia espacial.

O OSDR expõe uma API JSON pública (sem key) para buscar estudos e obter seus
metadados e manifestos de arquivos. Repassamos os endpoints GET somente leitura.
"""

from typing import Any

from fastapi import APIRouter, Path, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/osdr", tags=["OSDR - Open Science Data Repository"])

_BASE = settings.osdr_base_url


@router.get("/search", summary="Buscar estudos/datasets de biologia espacial")
async def search(
    term: str | None = Query(None, description="Termo de busca livre."),
    type: str | None = Query(None, description="Banco de dados (cgene, nih_geo_gse, ebi_pride...)."),
    size: int | None = Query(None, description="Quantidade de resultados."),
    from_: int | None = Query(None, alias="from", description="Deslocamento (paginação)."),
    sort: str | None = Query(None, description="Campo de ordenação."),
    order: str | None = Query(None, description="Direção (ASC/DESC)."),
) -> Any:
    """busca em texto completo no catálogo de estudos do OSDR"""
    return await fetch_json(
        f"{_BASE}/search",
        {
            "term": term,
            "type": type,
            "size": size,
            "from": from_,
            "sort": sort,
            "order": order,
        },
        with_api_key=False,
    )


@router.get("/meta/{study_id}", summary="Metadados de um estudo (OSD-<id>)")
async def study_meta(
    study_id: str = Path(..., description="ID numérico do estudo (ex.: 87)."),
) -> Any:
    """retorna o documento completo de metadados de um estudo do OSDR"""
    return await fetch_json(f"{_BASE}/osd/meta/{study_id}", with_api_key=False)


@router.get("/files/{study_ids}", summary="Manifesto de arquivos de um ou mais estudos")
async def study_files(
    study_ids: str = Path(..., description="ID(s) separados por vírgula (ex.: 87,137)."),
    page: int | None = Query(None, description="Página do manifesto."),
    size: int | None = Query(None, description="Itens por página."),
    all_files: bool | None = Query(None, description="Incluir arquivos ocultos."),
) -> Any:
    """retorna o manifesto de arquivos para download do(s) estudo(s) informado(s)"""
    return await fetch_json(
        f"{_BASE}/osd/files/{study_ids}",
        {"page": page, "size": size, "all_files": all_files},
        with_api_key=False,
    )
