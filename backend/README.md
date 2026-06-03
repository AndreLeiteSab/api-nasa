# Backend — NASA API Gateway (FastAPI)

Gateway stateless que intermedia o acesso às APIs abertas da NASA.

## Rodando

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # configure NASA_API_KEY
uvicorn app.main:app --reload
```

- Docs Swagger: <http://127.0.0.1:8000/docs>
- Docs ReDoc: <http://127.0.0.1:8000/redoc>
- Healthcheck: <http://127.0.0.1:8000/health>

Todas as rotas ficam sob o prefixo `/api/v1`.

## Arquitetura

| Camada | Responsabilidade |
|---|---|
| `config.py` | Lê variáveis de ambiente (chave, URLs, timeouts, CORS). |
| `core/nasa_client.py` | Cliente `httpx` assíncrono e compartilhado (pool de conexões). |
| `core/exceptions.py` | Normaliza erros upstream em um JSON consistente. |
| `routers/*` | Um módulo por serviço da NASA; cada rota é fina e documentada. |
| `main.py` | Cria o app, aplica CORS, registra routers e handlers. |

### Princípios

- **Sem persistência** — nada é armazenado, apenas repassado.
- **Assíncrono** — `httpx.AsyncClient` reutilizado entre requisições.
- **Erros previsíveis** — toda falha vira `{ "error": true, "status_code", "message" }`.
- **Modular** — adicionar um serviço = criar um router e listá-lo em `routers/__init__.py`.

## Exemplos de consumo

```bash
curl "http://127.0.0.1:8000/api/v1/apod"
curl "http://127.0.0.1:8000/api/v1/neows/feed?start_date=2024-01-01&end_date=2024-01-02"
curl "http://127.0.0.1:8000/api/v1/mars-rover/rovers/curiosity/photos?sol=1000&camera=NAVCAM"
curl "http://127.0.0.1:8000/api/v1/eonet/events?status=open&limit=5"
```

## Testes

```bash
pytest
```
