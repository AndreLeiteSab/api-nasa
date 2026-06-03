"""Smoke tests for the gateway.

The upstream NASA client is mocked so the suite runs offline and fast — we only
verify routing, parameter forwarding and error normalization, never NASA itself.
"""

import pytest
from fastapi.testclient import TestClient

import app.core.nasa_client as nasa_client
from app.core.exceptions import NasaAPIError
from app.main import app


@pytest.fixture
def client(monkeypatch):
    """TestClient with the NASA HTTP layer stubbed out."""

    async def fake_fetch_json(url, params=None, *, with_api_key=True):
        return {"url": url, "params": params or {}, "with_api_key": with_api_key}

    monkeypatch.setattr(nasa_client, "fetch_json", fake_fetch_json)
    # Routers imported the symbol directly, so patch it there too.
    for module in (
        "app.routers.apod",
        "app.routers.neows",
        "app.routers.donki",
        "app.routers.eonet",
        "app.routers.epic",
        "app.routers.mars_rover",
        "app.routers.image_library",
        "app.routers.techtransfer",
        "app.routers.insight",
        "app.routers.exoplanet",
        "app.routers.tle",
        "app.routers.ssd",
        "app.routers.earth",
    ):
        monkeypatch.setattr(f"{module}.fetch_json", fake_fetch_json, raising=False)

    with TestClient(app) as test_client:
        yield test_client


def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["service"]


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_apod_forwards_params(client):
    res = client.get("/api/v1/apod", params={"date": "2024-01-01"})
    assert res.status_code == 200
    body = res.json()
    assert body["params"]["date"] == "2024-01-01"
    assert "planetary/apod" in body["url"]


def test_neows_feed(client):
    res = client.get("/api/v1/neows/feed", params={"start_date": "2024-01-01"})
    assert res.status_code == 200
    assert "feed" in res.json()["url"]


def test_eonet_skips_api_key(client):
    res = client.get("/api/v1/eonet/events")
    assert res.json()["with_api_key"] is False


def test_error_handler(client, monkeypatch):
    async def boom(*args, **kwargs):
        raise NasaAPIError("falhou", status_code=502)

    monkeypatch.setattr("app.routers.apod.fetch_json", boom)
    res = client.get("/api/v1/apod")
    assert res.status_code == 502
    assert res.json()["error"] is True
