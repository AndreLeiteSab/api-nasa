"""SSD/CNEOS — JPL Solar System Dynamics & Center for NEO Studies (no API key)."""

from typing import Any

from fastapi import APIRouter, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/ssd", tags=["SSD/CNEOS - JPL"])

_BASE = settings.ssd_base_url


@router.get("/cad", summary="Close Approach Data (aproximações de NEOs)")
async def close_approach(
    date_min: str | None = Query(None, alias="date-min"),
    date_max: str | None = Query(None, alias="date-max"),
    dist_max: str | None = Query(None, alias="dist-max"),
    dist_min: str | None = Query(None, alias="dist-min"),
    body: str | None = Query(None),
    sort: str | None = Query(None),
    limit: int | None = Query(None),
    fullname: bool | None = Query(None),
) -> Any:
    return await fetch_json(
        f"{_BASE}/cad.api",
        {
            "date-min": date_min,
            "date-max": date_max,
            "dist-max": dist_max,
            "dist-min": dist_min,
            "body": body,
            "sort": sort,
            "limit": limit,
            "fullname": fullname,
        },
        with_api_key=False,
    )


@router.get("/fireball", summary="Bolas de fogo (fireballs) atmosféricas")
async def fireball(
    date_min: str | None = Query(None, alias="date-min"),
    date_max: str | None = Query(None, alias="date-max"),
    limit: int | None = Query(None),
    sort: str | None = Query(None),
) -> Any:
    return await fetch_json(
        f"{_BASE}/fireball.api",
        {"date-min": date_min, "date-max": date_max, "limit": limit, "sort": sort},
        with_api_key=False,
    )


@router.get("/sentry", summary="Sentry — monitoramento de risco de impacto")
async def sentry(
    spk: str | None = Query(None),
    des: str | None = Query(None),
    h_max: float | None = Query(None, alias="h-max"),
    ps_min: str | None = Query(None, alias="ps-min"),
    ip_min: float | None = Query(None, alias="ip-min"),
) -> Any:
    return await fetch_json(
        f"{_BASE}/sentry.api",
        {"spk": spk, "des": des, "h-max": h_max, "ps-min": ps_min, "ip-min": ip_min},
        with_api_key=False,
    )


@router.get("/scout", summary="Scout — objetos recém-descobertos")
async def scout(
    tdes: str | None = Query(None),
    orbits: bool | None = Query(None),
    n_orbits: int | None = Query(None, alias="n-orbits"),
) -> Any:
    return await fetch_json(
        f"{_BASE}/scout.api",
        {"tdes": tdes, "orbits": orbits, "n-orbits": n_orbits},
        with_api_key=False,
    )


@router.get("/nhats", summary="NHATS — alvos acessíveis por missões humanas")
async def nhats(
    des: str | None = Query(None),
    spk: str | None = Query(None),
    dv: int | None = Query(None),
    dur: int | None = Query(None),
) -> Any:
    return await fetch_json(
        f"{_BASE}/nhats.api",
        {"des": des, "spk": spk, "dv": dv, "dur": dur},
        with_api_key=False,
    )
