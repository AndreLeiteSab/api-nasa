"""Ponto de entrada da aplicação FastAPI do Gateway de APIs da NASA.

Este serviço é um proxy stateless na frente das APIs abertas da NASA: expõe um
router com prefixo próprio para cada serviço da NASA, injeta a API key, padroniza
os erros e aplica CORS para o frontend React consumir tudo a partir de uma única
origem.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.nasa_client import shutdown_client, startup_client
from app.routers import all_routers


@asynccontextmanager
async def lifespan(_: FastAPI):
    """garante que exista um único cliente HTTP reutilizável durante toda a execução"""
    await startup_client()
    yield
    await shutdown_client()

"""instância da aplicação FastAPI, com metadados para documentação"""
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Gateway FastAPI que intermedia o acesso às APIs abertas da NASA. "
        "Todas as rotas são somente leitura (GET) e nenhum dado é armazenado — "
        "o serviço apenas repassa as respostas da NASA ao frontend."
    ),
    lifespan=lifespan,
)

# configura CORS - permitir que o frontend acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# monta os routers com o prefixo comum /api/v1
API_PREFIX = "/api/v1"
for router in all_routers:
    app.include_router(router, prefix=API_PREFIX)


@app.get("/", tags=["Meta"], summary="Informações do serviço")
async def root() -> dict:
    """endpoint básico que retorna metadados do serviço"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "api_prefix": API_PREFIX,
    }


@app.get("/health", tags=["Meta"], summary="Healthcheck")
async def health() -> dict:
    """endpoint de healthcheck para monitoramento"""
    return {"status": "ok"}
