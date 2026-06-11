"""TechTransfer — patentes, software e tecnologias spinoff da NASA."""

from typing import Any

from fastapi import APIRouter, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/techtransfer", tags=["TechTransfer - Patentes e Software"])

_BASE = f"{settings.nasa_base_url}/techtransfer"


@router.get("/patent", summary="Buscar patentes")
async def get_patents(
    query: str | None = Query(None, description="Termo de busca (ex.: engine)."),
) -> Any:
    # a NASA usa o termo de busca como chave de query "pura", ex.: ?engine
    params = {query: ""} if query else None
    return await fetch_json(f"{_BASE}/patent/", params)


@router.get("/patent-issued", summary="Buscar patentes emitidas")
async def get_patents_issued(query: str | None = Query(None)) -> Any:
    params = {query: ""} if query else None
    return await fetch_json(f"{_BASE}/patent_issued/", params)


@router.get("/software", summary="Buscar software da NASA")
async def get_software(query: str | None = Query(None)) -> Any:
    params = {query: ""} if query else None
    return await fetch_json(f"{_BASE}/software/", params)


@router.get("/spinoff", summary="Buscar tecnologias spinoff")
async def get_spinoff(query: str | None = Query(None)) -> Any:
    params = {query: ""} if query else None
    return await fetch_json(f"{_BASE}/spinoff/", params)
