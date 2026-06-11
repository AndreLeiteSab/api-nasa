"""Testes de fumaça (smoke tests) do gateway.

O cliente da NASA é mockado para a suíte rodar offline e rápido — verificamos
apenas roteamento, repasse de parâmetros e padronização de erros, nunca a NASA em si.
"""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

import app.core.nasa_client as nasa_client
from app.core.exceptions import NasaAPIError
from app.main import app


class FakeClient:
    """substituto mínimo do httpx.AsyncClient que devolve respostas pré-definidas"""

    def __init__(self, responses):
        self._responses = responses
        self.calls = 0

    async def get(self, url, params=None, headers=None):
        response = self._responses[self.calls]
        self.calls += 1
        return response


@pytest.fixture
def client(monkeypatch):
    """TestClient com a camada HTTP da NASA substituída por um stub"""

    async def fake_fetch_json(url, params=None, *, with_api_key=True, headers=None):
        return {
            "url": url,
            "params": params or {},
            "with_api_key": with_api_key,
            "headers": headers,
        }

    monkeypatch.setattr(nasa_client, "fetch_json", fake_fetch_json)
    # os routers importaram o símbolo direto, então faz o patch lá também
    for module in (
        "app.routers.apod",
        "app.routers.neows",
        "app.routers.donki",
        "app.routers.eonet",
        "app.routers.epic",
        "app.routers.image_library",
        "app.routers.techtransfer",
        "app.routers.insight",
        "app.routers.exoplanet",
        "app.routers.tle",
        "app.routers.ssd",
        "app.routers.osdr",
        "app.routers.ssc",
        "app.routers.techport",
        "app.routers.trek",
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


def test_osdr_search_skips_api_key(client):
    res = client.get("/api/v1/osdr/search", params={"term": "space"})
    body = res.json()
    assert "osdr/data/search" in body["url"]
    assert body["with_api_key"] is False


def test_ssc_observatories_requests_json(client):
    res = client.get("/api/v1/ssc/observatories")
    body = res.json()
    assert "observatories" in body["url"]
    assert body["headers"] == {"Accept": "application/json"}


def test_techport_uses_api_key(client):
    res = client.get("/api/v1/techport/projects")
    assert res.json()["with_api_key"] is True


def test_trek_search_resolves_body(client):
    res = client.get("/api/v1/trek/mars/search")
    assert "/mars/TrekServices" in res.json()["url"]


def test_trek_rejects_unknown_body(client):
    res = client.get("/api/v1/trek/pluto/search")
    assert res.status_code == 404


def test_exoplanet_builds_adql_query(client):
    """os campos do formulário são montados em uma query ADQL para o serviço TAP"""
    res = client.get(
        "/api/v1/exoplanet",
        params={"select": "pl_name,hostname", "where": "disc_year>2020", "order": "disc_year desc"},
    )
    body = res.json()
    assert "TAP/sync" in body["url"]
    assert body["with_api_key"] is False
    assert body["params"]["query"] == (
        "select top 100 pl_name,hostname from ps where disc_year>2020 order by disc_year desc"
    )


def test_epic_enriches_metadata_with_image_urls(client, monkeypatch):
    """cada registro EPIC deve ganhar links de thumbnail/resolução cheia relativos ao gateway"""

    async def fake_metadata(url, params=None, *, with_api_key=True, headers=None):
        return [{"image": "epic_1b_20260608005515", "date": "2026-06-08 00:50:27"}]

    monkeypatch.setattr("app.routers.epic.fetch_json", fake_metadata)
    record = client.get("/api/v1/epic/natural").json()[0]
    base = "/api/v1/epic/natural/image/2026-06-08/epic_1b_20260608005515"
    assert record["image_url"] == f"{base}?fmt=thumbs"
    assert record["image_url_hd"] == base
    # a api_key nunca pode vazar nos links entregues ao navegador
    assert "api_key" not in record["image_url"]


def test_epic_image_proxy_streams_bytes(client, monkeypatch):
    """o proxy monta a URL assinada do arquivo no servidor e repassa os bytes"""
    captured = {}

    async def fake_bytes(url, params=None, *, with_api_key=True):
        captured["url"] = url
        return b"PNGDATA", "image/png"

    monkeypatch.setattr("app.routers.epic.fetch_bytes", fake_bytes)
    res = client.get("/api/v1/epic/natural/image/2026-06-08/epic_1b_20260608005515")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert res.content == b"PNGDATA"
    assert captured["url"].startswith(
        "https://api.nasa.gov/EPIC/archive/natural/2026/06/08/png/"
        "epic_1b_20260608005515.png"
    )
    assert "api_key=" in captured["url"]


def test_request_preserves_url_query_when_no_params(monkeypatch):
    """uma query string já assinada na URL precisa sobreviver a um params vazio

    o httpx apaga a query da URL quando recebe um ``params`` explícito, então
    precisamos passar ``None`` (e não ``{}``) — senão links já assinados, como o do
    arquivo do EPIC, perdem a ``api_key`` e a NASA responde 403.
    """

    class CapturingClient:
        def __init__(self):
            self.params = "unset"

        async def get(self, url, params=None, headers=None):
            self.params = params
            return httpx.Response(200, json={"ok": True})

    fake = CapturingClient()
    monkeypatch.setattr(nasa_client, "_client", fake)

    asyncio.run(
        nasa_client.fetch_bytes(
            "https://api.nasa.gov/EPIC/archive/x.jpg?api_key=SECRET",
            with_api_key=False,
        )
    )
    assert fake.params is None


def test_request_retries_transient_5xx(monkeypatch):
    """uma falha momentânea 503 deve ser repetida e o 200 final retornado"""
    responses = [httpx.Response(503, text="down"), httpx.Response(200, json={"ok": True})]
    fake = FakeClient(responses)
    monkeypatch.setattr(nasa_client, "_client", fake)

    async def no_sleep(_seconds):
        return None

    monkeypatch.setattr(nasa_client.asyncio, "sleep", no_sleep)

    result = asyncio.run(nasa_client.fetch_json("https://nasa/test", with_api_key=False))
    assert result == {"ok": True}
    assert fake.calls == 2  # uma falha + um sucesso


def test_request_gives_up_after_retries(monkeypatch):
    """um 5xx persistente é padronizado em 502 após esgotar as tentativas"""
    fake = FakeClient([httpx.Response(503) for _ in range(5)])
    monkeypatch.setattr(nasa_client, "_client", fake)

    async def no_sleep(_seconds):
        return None

    monkeypatch.setattr(nasa_client.asyncio, "sleep", no_sleep)

    with pytest.raises(NasaAPIError) as exc_info:
        asyncio.run(nasa_client.fetch_json("https://nasa/test", with_api_key=False))
    assert exc_info.value.status_code == 502
    assert fake.calls == 3  # tentativa inicial + 2 retentativas


def test_rate_limit_message():
    """um 429 exibe uma mensagem clara e acionável e mantém o status 429"""
    resp = httpx.Response(429, json={"error": {"code": "OVER_RATE_LIMIT"}})
    with pytest.raises(NasaAPIError) as exc_info:
        nasa_client._raise_for_status(resp)
    assert exc_info.value.status_code == 429
    assert "rate limit" in exc_info.value.message.lower()


def test_error_handler(client, monkeypatch):
    async def boom(*args, **kwargs):
        raise NasaAPIError("falhou", status_code=502)

    monkeypatch.setattr("app.routers.apod.fetch_json", boom)
    res = client.get("/api/v1/apod")
    assert res.status_code == 502
    assert res.json()["error"] is True
