"""Cliente HTTP assíncrono usado para repassar as requisições aos serviços da NASA.

Um único ``httpx.AsyncClient`` compartilhado é criado na inicialização da
aplicação e reaproveitado em todas as requisições (pool de conexões = mais
desempenho). O cliente é um proxy fino e stateless: encaminha a requisição,
padroniza os erros e devolve a resposta da NASA sem armazenar nada.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.config import settings
from app.core.exceptions import NasaAPIError

# cliente HTTP global do módulo
_client: httpx.AsyncClient | None = None

# três valores de retry servem para lidar com falhas temporárias
_RETRYABLE_STATUS = {502, 503, 504}
_MAX_RETRIES = 2
_RETRY_BACKOFF = 0.5  


async def startup_client() -> None:
    """cria o cliente HTTP compartilhado quando a aplicação inicia"""
    global _client
    if _client is None:
        limits = httpx.Limits(max_connections=settings.max_connections)
        _client = httpx.AsyncClient(
            timeout=settings.request_timeout,
            limits=limits,
            follow_redirects=True,
            headers={"User-Agent": f"{settings.app_name}/{settings.app_version}"},
        )


async def shutdown_client() -> None:
    """fecha o cliente quando a aplicação encerra"""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _get_client() -> httpx.AsyncClient:
    if _client is None:
        raise NasaAPIError("Cliente HTTP não inicializado.", status_code=503)
    return _client


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any]:
    """remove parâmetros com valor None para evitar enviar "param=None" """
    if not params:
        return {}
    return {key: value for key, value in params.items() if value is not None}

# monta a query final combinando os parâmetros do endpoint com a chave API
def _build_query(
    params: dict[str, Any] | None, with_api_key: bool
) -> dict[str, Any]:
    query = _clean_params(params)
    if with_api_key:
        query.setdefault("api_key", settings.nasa_api_key)
    return query


async def _request(
    url: str, query: dict[str, Any], headers: dict[str, str] | None
) -> httpx.Response:
    """faz o GET na NASA, tentando de novo quando a falha é temporária

    Erros de conexão e status 5xx repetíveis são tentados de novo com uma
    pequena espera; timeout e os demais status retornam/sobem na hora.
    """
    client = _get_client()
    # usa None (e não um dict vazio) quando não há parâmetros: o httpx trata o
    # params como definitivo e apagaria qualquer query já presente na url
    # (ex.: uma api_key já embutida)
    request_params = query or None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = await client.get(url, params=request_params, headers=headers)
        except httpx.TimeoutException as exc:
            raise NasaAPIError(
                "Tempo de resposta da NASA excedido (timeout).", status_code=504
            ) from exc
        except httpx.RequestError as exc:
            if attempt < _MAX_RETRIES:
                await asyncio.sleep(_RETRY_BACKOFF * (attempt + 1))
                continue
            raise NasaAPIError(
                f"Falha ao conectar com a NASA: {exc.__class__.__name__}.",
                status_code=502,
            ) from exc

        if response.status_code in _RETRYABLE_STATUS and attempt < _MAX_RETRIES:
            await asyncio.sleep(_RETRY_BACKOFF * (attempt + 1))
            continue
        return response

    return response  


def _raise_for_status(response: httpx.Response) -> None:
    """transforma respostas de erro da NASA em um erro mais amigável da aplicação"""
    status = response.status_code
    try:
        upstream: Any = response.json()
    except ValueError:
        upstream = response.text[:500]

    if status == 429:
        raise NasaAPIError(
            "Limite de requisições da NASA atingido (rate limit). Configure uma "
            "NASA_API_KEY própria no .env — a DEMO_KEY tem cota baixa.",
            status_code=429,
            upstream=upstream,
        )
    raise NasaAPIError(
        f"A NASA retornou um erro ({status}).",
        status_code=status if status < 500 else 502,
        upstream=upstream,
    )


async def fetch_json(
    url: str,
    params: dict[str, Any] | None = None,
    *,
    with_api_key: bool = True,
    headers: dict[str, str] | None = None,
) -> Any:
    """faz um GET e retorna o corpo JSON já decodificado

    Parâmetros:
        url: URL completa do serviço da NASA.
        params: Parâmetros de query (valores None são removidos automaticamente).
        with_api_key: Se deve injetar o parâmetro ``api_key`` da NASA.
        headers: Cabeçalhos extras opcionais (ex.: ``Accept: application/json``,
            exigido pelo serviço Satellite Situation Center).

    Lança:
        NasaAPIError: Em erros HTTP, timeout, falha de conexão ou JSON inválido.
    """
    response = await _request(url, _build_query(params, with_api_key), headers)
    if response.status_code >= 400:
        _raise_for_status(response)

    try:
        return response.json()
    except ValueError as exc:
        raise NasaAPIError(
            "Resposta da NASA não é um JSON válido.", status_code=502
        ) from exc


async def fetch_bytes(
    url: str,
    params: dict[str, Any] | None = None,
    *,
    with_api_key: bool = True,
) -> tuple[bytes, str]:
    """faz um GET e retorna os bytes brutos junto com o content type

    Usado em endpoints binários, como as imagens da Terra e do EPIC.

    Retorna:
        Tupla (content_bytes, content_type).
    """
    response = await _request(url, _build_query(params, with_api_key), None)
    if response.status_code >= 400:
        _raise_for_status(response)

    content_type = response.headers.get("content-type", "application/octet-stream")
    return response.content, content_type


async def fetch_text(
    url: str,
    params: dict[str, Any] | None = None,
    *,
    with_api_key: bool = False,
) -> tuple[str, str]:
    """faz um GET e retorna o texto decodificado junto com o content type

    Usado em endpoints de metadados não-JSON, como os documentos XML
    ``GetCapabilities`` (WMTS) expostos pelo GIBS e pelos serviços Trek.

    Retorna:
        Tupla (text_body, content_type).
    """
    response = await _request(url, _build_query(params, with_api_key), None)
    if response.status_code >= 400:
        _raise_for_status(response)

    content_type = response.headers.get("content-type", "text/plain")
    return response.text, content_type
