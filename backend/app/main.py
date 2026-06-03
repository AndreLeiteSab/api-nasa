"""FastAPI application entry point for the NASA API Gateway.

This service is a stateless proxy in front of NASA's open APIs: it exposes one
namespaced router per NASA service, injects the API key, normalizes errors and
applies CORS so the React frontend can consume everything from a single origin.
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
    """Manage the shared HTTP client lifecycle (startup/shutdown)."""
    await startup_client()
    yield
    await shutdown_client()


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

# CORS so the Vite frontend (localhost:5173) can call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# Mount every NASA service under the /api/v1 prefix.
API_PREFIX = "/api/v1"
for router in all_routers:
    app.include_router(router, prefix=API_PREFIX)


@app.get("/", tags=["Meta"], summary="Informações do serviço")
async def root() -> dict:
    """Basic service metadata and pointer to the docs."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "api_prefix": API_PREFIX,
    }


@app.get("/health", tags=["Meta"], summary="Healthcheck")
async def health() -> dict:
    """Liveness probe."""
    return {"status": "ok"}
