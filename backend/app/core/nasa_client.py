"""Async HTTP client used to proxy requests to the NASA upstream services.

A single shared ``httpx.AsyncClient`` is created at application startup and reused
for every request (connection pooling = better performance). The client is a
thin, stateless proxy: it forwards the request, normalizes errors, and returns
the upstream payload without persisting anything.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.core.exceptions import NasaAPIError

# Module-level singleton, initialized during the app lifespan.
_client: httpx.AsyncClient | None = None


async def startup_client() -> None:
    """Create the shared AsyncClient. Called on app startup."""
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
    """Close the shared AsyncClient. Called on app shutdown."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _get_client() -> httpx.AsyncClient:
    if _client is None:
        raise NasaAPIError("Cliente HTTP não inicializado.", status_code=503)
    return _client


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any]:
    """Drop keys whose value is None so we don't forward empty query params."""
    if not params:
        return {}
    return {key: value for key, value in params.items() if value is not None}


async def fetch_json(
    url: str,
    params: dict[str, Any] | None = None,
    *,
    with_api_key: bool = True,
) -> Any:
    """Perform a GET request and return the decoded JSON body.

    Args:
        url: Fully-qualified upstream URL.
        params: Query parameters (None values are stripped automatically).
        with_api_key: Whether to inject the NASA ``api_key`` query parameter.

    Raises:
        NasaAPIError: On HTTP errors, timeouts, connection issues or invalid JSON.
    """
    client = _get_client()
    query = _clean_params(params)
    if with_api_key:
        query.setdefault("api_key", settings.nasa_api_key)

    try:
        response = await client.get(url, params=query)
    except httpx.TimeoutException as exc:
        raise NasaAPIError(
            "Tempo de resposta da NASA excedido (timeout).", status_code=504
        ) from exc
    except httpx.RequestError as exc:
        raise NasaAPIError(
            f"Falha ao conectar com a NASA: {exc.__class__.__name__}.",
            status_code=502,
        ) from exc

    if response.status_code >= 400:
        # Forward a clean version of the upstream error.
        upstream: Any
        try:
            upstream = response.json()
        except ValueError:
            upstream = response.text[:500]
        raise NasaAPIError(
            f"A NASA retornou um erro ({response.status_code}).",
            status_code=response.status_code if response.status_code < 500 else 502,
            upstream=upstream,
        )

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
    """Perform a GET request and return raw bytes plus the content type.

    Used for binary endpoints such as Earth imagery and EPIC images.

    Returns:
        Tuple of (content_bytes, content_type).
    """
    client = _get_client()
    query = _clean_params(params)
    if with_api_key:
        query.setdefault("api_key", settings.nasa_api_key)

    try:
        response = await client.get(url, params=query)
    except httpx.TimeoutException as exc:
        raise NasaAPIError(
            "Tempo de resposta da NASA excedido (timeout).", status_code=504
        ) from exc
    except httpx.RequestError as exc:
        raise NasaAPIError(
            f"Falha ao conectar com a NASA: {exc.__class__.__name__}.",
            status_code=502,
        ) from exc

    if response.status_code >= 400:
        raise NasaAPIError(
            f"A NASA retornou um erro ({response.status_code}).",
            status_code=response.status_code if response.status_code < 500 else 502,
            upstream=response.text[:500],
        )

    content_type = response.headers.get("content-type", "application/octet-stream")
    return response.content, content_type
