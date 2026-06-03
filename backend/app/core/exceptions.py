"""Custom exceptions and centralized error handling for the gateway.

Errors coming from the upstream NASA APIs are normalized into a consistent JSON
shape so the frontend always receives a predictable payload.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class NasaAPIError(Exception):
    """Raised when an upstream NASA service returns an error or is unreachable.

    Attributes:
        message: Human-readable description of what went wrong.
        status_code: HTTP status code to return to the client.
        upstream: Optional raw payload returned by the upstream service.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_502_BAD_GATEWAY,
        upstream: object | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.upstream = upstream


def _error_payload(message: str, status_code: int, upstream: object | None = None) -> dict:
    """Build the standardized error response body."""
    body: dict = {
        "error": True,
        "status_code": status_code,
        "message": message,
    }
    if upstream is not None:
        body["upstream"] = upstream
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the gateway's exception handlers to the FastAPI app."""

    @app.exception_handler(NasaAPIError)
    async def nasa_api_error_handler(_: Request, exc: NasaAPIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.message, exc.status_code, exc.upstream),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        # Last-resort safety net so we never leak stack traces to the client.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(
                "Erro interno inesperado no gateway.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )
