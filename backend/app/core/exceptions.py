"""Exceções personalizadas e tratamento centralizado de erros do gateway.

Os erros vindos das APIs da NASA são padronizados em um formato JSON consistente
para que o frontend sempre receba uma resposta previsível.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class NasaAPIError(Exception):
    """Lançada quando um serviço da NASA retorna erro ou está inacessível.

    Atributos:
        message: Descrição legível do que deu errado.
        status_code: Código HTTP a devolver para o cliente.
        upstream: Resposta original do serviço da NASA (opcional).
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
    """monta o corpo padronizado da resposta de erro"""
    body: dict = {
        "error": True,
        "status_code": status_code,
        "message": message,
    }
    if upstream is not None:
        body["upstream"] = upstream
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """registra os tratadores de exceção do gateway na aplicação FastAPI"""

    @app.exception_handler(NasaAPIError)
    async def nasa_api_error_handler(_: Request, exc: NasaAPIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.message, exc.status_code, exc.upstream),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        # rede de segurança final para nunca vazar stack traces ao cliente
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(
                "Erro interno inesperado no gateway.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )
