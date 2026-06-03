"""DONKI — Space Weather Database Of Notifications, Knowledge, Information.

Every DONKI sub-resource shares the same ``startDate`` / ``endDate`` filtering
pattern, so they are generated from a small table to keep the module DRY while
still exposing one explicit, documented endpoint per resource.
"""

from typing import Any

from fastapi import APIRouter, Query

from app.config import settings
from app.core.nasa_client import fetch_json

router = APIRouter(prefix="/donki", tags=["DONKI - Clima Espacial"])

_BASE = f"{settings.nasa_base_url}/DONKI"


async def _date_ranged(resource: str, start_date: str | None, end_date: str | None) -> Any:
    """Helper for the many DONKI endpoints that only filter by date range."""
    return await fetch_json(
        f"{_BASE}/{resource}",
        {"startDate": start_date, "endDate": end_date},
    )


@router.get("/cme", summary="Coronal Mass Ejection (CME)")
async def get_cme(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> Any:
    return await _date_ranged("CME", start_date, end_date)


@router.get("/cme-analysis", summary="CME Analysis")
async def get_cme_analysis(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    most_accurate_only: bool | None = Query(None),
    complete_entry_only: bool | None = Query(None),
    speed: int | None = Query(None),
    half_angle: int | None = Query(None),
    catalog: str | None = Query(None),
    keyword: str | None = Query(None),
) -> Any:
    return await fetch_json(
        f"{_BASE}/CMEAnalysis",
        {
            "startDate": start_date,
            "endDate": end_date,
            "mostAccurateOnly": most_accurate_only,
            "completeEntryOnly": complete_entry_only,
            "speed": speed,
            "halfAngle": half_angle,
            "catalog": catalog,
            "keyword": keyword,
        },
    )


@router.get("/gst", summary="Geomagnetic Storm (GST)")
async def get_gst(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> Any:
    return await _date_ranged("GST", start_date, end_date)


@router.get("/ips", summary="Interplanetary Shock (IPS)")
async def get_ips(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    location: str | None = Query(None),
    catalog: str | None = Query(None),
) -> Any:
    return await fetch_json(
        f"{_BASE}/IPS",
        {
            "startDate": start_date,
            "endDate": end_date,
            "location": location,
            "catalog": catalog,
        },
    )


@router.get("/flr", summary="Solar Flare (FLR)")
async def get_flr(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> Any:
    return await _date_ranged("FLR", start_date, end_date)


@router.get("/sep", summary="Solar Energetic Particle (SEP)")
async def get_sep(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> Any:
    return await _date_ranged("SEP", start_date, end_date)


@router.get("/mpc", summary="Magnetopause Crossing (MPC)")
async def get_mpc(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> Any:
    return await _date_ranged("MPC", start_date, end_date)


@router.get("/rbe", summary="Radiation Belt Enhancement (RBE)")
async def get_rbe(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> Any:
    return await _date_ranged("RBE", start_date, end_date)


@router.get("/hss", summary="High Speed Stream (HSS)")
async def get_hss(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> Any:
    return await _date_ranged("HSS", start_date, end_date)


@router.get("/wsa-enlil", summary="WSA+EnlilSimulations")
async def get_wsa_enlil(
    start_date: str | None = Query(None), end_date: str | None = Query(None)
) -> Any:
    return await _date_ranged("WSAEnlilSimulations", start_date, end_date)


@router.get("/notifications", summary="Notificações DONKI")
async def get_notifications(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    type: str | None = Query(None, description="Tipo: all, FLR, SEP, CME, IPS, MPC, GST, RBE, report."),
) -> Any:
    return await fetch_json(
        f"{_BASE}/notifications",
        {"startDate": start_date, "endDate": end_date, "type": type},
    )
