# CLAUDE.md — NASA API Explorer

Instruções específicas deste projeto para o Claude Code.

## Visão geral

Trabalho acadêmico (UNICV). Aplicação full-stack que consome **todas as rotas GET**
das APIs abertas da NASA. O front-end **nunca** acessa a NASA diretamente — tudo
passa pelo gateway FastAPI.

## Stack

- **Backend:** FastAPI + httpx (async), Python 3.11+
- **Frontend:** React 18 + Vite
- **Sem banco de dados** — o gateway é stateless (proibido armazenar dados da NASA).

## Regras do projeto

1. Apenas métodos **GET** (sem POST/PUT/DELETE).
2. O gateway **não armazena** dados — só repassa.
3. O front-end consome **somente** o backend, nunca `api.nasa.gov`.
4. A `NASA_API_KEY` vive apenas no `backend/.env` (nunca versionar).
5. Adicionar um serviço novo: criar `backend/app/routers/<nome>.py` e registrá-lo
   em `routers/__init__.py`; depois adicionar a entrada em
   `frontend/src/services/endpoints.js`.

## Comandos úteis

```bash
# Backend
cd backend && uvicorn app.main:app --reload
cd backend && pytest

# Frontend
cd frontend && npm run dev
```

## Convenções

- Rotas sob `/api/v1`, uma tag/Swagger por serviço.
- Erros sempre no formato `{ "error": true, "status_code", "message" }`.
- Parâmetros opcionais com valor `None` são removidos antes de chamar a NASA.
- Comentários e docstrings de código em pt-BR; termos técnicos (endpoint, query,
  proxy, gateway, rate limit, timeout, WMTS, etc.) mantidos em inglês. UI e docs em pt-BR.
