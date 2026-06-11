"""Exoplanet Archive — consulta os datasets de exoplanetas via serviço TAP (sem key).

A interface antiga ``nph-nstedAPI`` (e sua tabela ``exoplanets``) foi descontinuada
pela Caltech. A API atual é um endpoint TAP que recebe uma ``query`` em ADQL. Para
manter funcionando o formulário simples de tabela/select/where do frontend, montamos
aqui a instrução ADQL a partir desses parâmetros.
"""

from typing import Any

from fastapi import APIRouter, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/exoplanet", tags=["Exoplanet Archive"])

_URL = settings.exoplanet_base_url


@router.get("", summary="Consultar arquivo de exoplanetas (TAP/ADQL)")
async def query_exoplanets(
    table: str = Query("ps", description="Tabela TAP (ex.: ps, pscomppars)."),
    select: str | None = Query(None, description="Colunas (ADQL SELECT). Padrão: todas (*)."),
    where: str | None = Query(None, description="Cláusula WHERE em ADQL (ex.: disc_year>2020)."),
    order: str | None = Query(None, description="Cláusula ORDER BY (ex.: disc_year desc)."),
    limit: int | None = Query(100, description="Máx. de linhas (TOP). Use 0 para sem limite."),
    format: str = Query("json", description="Formato de saída (json, csv, votable...)."),
) -> Any:
    """monta uma query ADQL a partir dos campos do formulário e repassa ao serviço TAP"""
    top = f"top {limit} " if limit else ""
    adql = f"select {top}{select or '*'} from {table}"
    if where:
        adql += f" where {where}"
    if order:
        adql += f" order by {order}"
    return await fetch_json(
        _URL,
        {"query": adql, "format": format},
        with_api_key=False,
    )
