"""Techport — dados legíveis por máquina de projetos de tecnologia da NASA (exige API key)."""

from typing import Any

from fastapi import APIRouter, Path, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/techport", tags=["Techport - Projetos de tecnologia"])

_BASE = settings.techport_base_url
_JSON_HEADERS = {"Accept": "application/json"}


@router.get("/projects", summary="Listar projetos (IDs) atualizados desde uma data")
async def list_projects(
    updated_since: str | None = Query(
        None, alias="updatedSince", description="Filtra projetos atualizados a partir de YYYY-MM-DD."
    ),
) -> Any:
    """retorna a lista de IDs de projetos do Techport (com filtro opcional por data)"""
    return await fetch_json(
        f"{_BASE}/projects",
        {"updatedSince": updated_since},
        headers=_JSON_HEADERS,
    )


@router.get("/projects/{project_id}", summary="Detalhes de um projeto de tecnologia")
async def get_project(
    project_id: int = Path(..., description="ID numérico do projeto Techport."),
) -> Any:
    """retorna o registro completo de detalhes de um projeto do Techport"""
    return await fetch_json(f"{_BASE}/projects/{project_id}", headers=_JSON_HEADERS)
