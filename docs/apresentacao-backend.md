# Backend NASA API Gateway — Explicação Completa

> Material de apoio para a apresentação na matéria **Programação para Internet: Web Services e APIs**.
> Projeto: gateway **FastAPI** que intermedia o acesso às APIs abertas da NASA.
> **18 serviços** da NASA expostos em **64 endpoints GET**, todos atrás de um único gateway.

---

## Sumário

1. [O conceito central: o que é esse backend?](#1-o-conceito-central-o-que-é-esse-backend)
2. [Arquitetura em camadas](#2-arquitetura-em-camadas)
3. [Estrutura dos endpoints](#3-estrutura-dos-endpoints)
4. [Como os GETs são feitos](#4-como-os-gets-são-feitos--o-coração-da-explicação)
5. [Tratamento de erros](#5-tratamento-de-erros--uniformidade)
6. [Conceitos de Web Services e APIs demonstrados](#6-conceitos-de-web-services-e-apis-que-o-projeto-demonstra)
7. [Fluxo completo de uma requisição](#7-fluxo-completo-de-uma-requisição)
8. [Como rodar e testar](#8-como-rodar-e-testar)

---

## 1. O conceito central: o que é esse backend?

Esse backend é um **API Gateway** (também chamado de *proxy* ou *Backend-for-Frontend*).
Ele **não é** a "API da NASA" — ele fica **no meio**, entre o front-end React e as APIs
públicas da NASA.

```
┌──────────┐      HTTP       ┌─────────────────┐      HTTP       ┌──────────────┐
│ Frontend │  ───────────▶   │  SEU GATEWAY    │  ───────────▶   │  APIs NASA   │
│  React   │   /api/v1/...   │    (FastAPI)    │  api.nasa.gov   │ (18 serviços)│
│          │  ◀───────────   │                 │  ◀───────────   │              │
└──────────┘   JSON limpo    └─────────────────┘   JSON cru      └──────────────┘
```

### Por que existe um gateway no meio?

Três motivos centrais em uma disciplina de Web Services:

1. **Segurança** — a `NASA_API_KEY` fica **só no servidor** (`backend/app/config.py`).
   O navegador nunca a vê. Se o front chamasse a NASA direto, a chave estaria exposta
   no código do cliente.
2. **CORS / origem única** — o front fala com **um só servidor**, na mesma origem, em vez
   de 18 domínios diferentes da NASA (cada um com regras de CORS próprias).
3. **Padronização** — erros, formatos e autenticação ficam **uniformes**, mesmo a NASA
   tendo serviços com comportamentos diferentes (uns pedem chave, outros não; uns
   devolvem JSON, outros XML, outros imagem binária).

> **Regra de ouro do projeto:** o gateway é **stateless** — não tem banco de dados,
> **não armazena nada**. Ele só **repassa** (proxy). E só aceita método **GET**
> (somente leitura).

---

## 2. Arquitetura em camadas

O código é separado por responsabilidade — isso é o que torna o projeto fácil de manter
e estender:

| Camada | Arquivo | Responsabilidade |
|---|---|---|
| **Entrada** | `app/main.py` | Cria o app, aplica CORS, registra os 18 routers e os handlers de erro |
| **Configuração** | `app/config.py` | Lê variáveis de ambiente (chave, URLs, timeouts) |
| **Cliente HTTP** | `app/core/nasa_client.py` | O "motor": faz os GETs para a NASA com `httpx` assíncrono |
| **Erros** | `app/core/exceptions.py` | Normaliza qualquer falha num JSON previsível |
| **Rotas** | `app/routers/` | **Um arquivo por serviço** da NASA (apod, neows, mars_rover...) |

A ideia: cada camada tem **um trabalho só**. A rota não sabe fazer HTTP; o cliente HTTP
não conhece as rotas; a config não conhece nenhuma das duas. Isso é **separação de
responsabilidades** (*separation of concerns*).

### Tecnologias (requirements.txt)

- **FastAPI** — framework web assíncrono e moderno (gera documentação OpenAPI sozinho).
- **httpx** — cliente HTTP assíncrono (o "navegador" do servidor para falar com a NASA).
- **pydantic / pydantic-settings** — validação de tipos e leitura de configuração.
- **uvicorn** — servidor ASGI que roda a aplicação.
- **pytest / pytest-asyncio** — testes.

---

## 3. Estrutura dos endpoints

### Prefixo e versionamento

Todos os endpoints vivem sob **`/api/v1`** (`app/main.py`). O `v1` é **versionamento de
API** — uma boa prática: se um dia o contrato mudar, cria-se `/api/v2` sem quebrar quem
já usa o `v1`.

### Cada serviço é um "router" com seu próprio prefixo

No `app/routers/__init__.py` existe uma lista `all_routers`, e o `main.py` faz um loop
incluindo todos:

```python
for router in all_routers:
    app.include_router(router, prefix=API_PREFIX)   # /api/v1 + prefixo do router
```

Então a URL final se monta em camadas:

```
/api/v1   +   /neows   +   /feed        →   GET /api/v1/neows/feed
  │             │            │
prefixo      prefixo do    rota dentro
global       router        do router
```

### Mapa dos 18 serviços (64 endpoints)

| # | Serviço | Prefixo | Endpoints | O que entrega |
|---|---|---|---|---|
| 1 | APOD | `/apod` | 1 | Imagem astronômica do dia |
| 2 | NeoWs | `/neows` | 3 | Asteroides próximos da Terra |
| 3 | DONKI | `/donki` | 11 | Clima espacial (tempestades solares) |
| 4 | Earth | `/earth` | 2 | Imagens de satélite Landsat |
| 5 | EONET | `/eonet` | 6 | Eventos naturais (incêndios, vulcões) |
| 6 | EPIC | `/epic` | 5 | Fotos da Terra inteira (satélite DSCOVR) |
| 7 | Mars Rover | `/mars-rover` | 5 | Fotos dos rovers em Marte |
| 8 | Image Library | `/image-library` | 5 | Acervo de mídia da NASA |
| 9 | TechTransfer | `/techtransfer` | 4 | Patentes e tecnologias |
| 10 | InSight | `/insight` | 1 | Clima em Marte |
| 11 | Exoplanet | `/exoplanet` | 1 | Catálogo de exoplanetas |
| 12 | TLE | `/tle` | 2 | Órbitas de satélites |
| 13 | SSD | `/ssd` | 5 | Dados de pequenos corpos (JPL) |
| 14 | GIBS | `/gibs` | 3 | Tiles de mapas de satélite (WMTS) |
| 15 | OSDR | `/osdr` | 3 | Dados de biologia espacial |
| 16 | SSC | `/ssc` | 2 | Posição de naves espaciais |
| 17 | TechPort | `/techport` | 2 | Projetos de tecnologia |
| 18 | Trek | `/trek` | 3 | Mapas de Lua/Marte/Vesta |

Além disso, há 2 rotas "meta" **fora** do `/api/v1`:

- **`GET /`** — informações do serviço (versão, link das docs).
- **`GET /health`** — *healthcheck* (verificação de que o serviço está no ar).

### Tags e documentação automática

Cada router declara uma **tag** (ex.: `tags=["NeoWs - Asteroides..."]`). O FastAPI usa
isso para gerar o **Swagger automático** em `/docs` e o **ReDoc** em `/redoc`, agrupando
os endpoints por serviço. Basta abrir `/docs` no navegador para ter documentação
interativa pronta — excelente para a apresentação ao vivo.

---

## 4. Como os GETs são feitos — o coração da explicação

Existem **dois níveis**: a **rota** (declarativa, fina) e o **cliente HTTP** (o motor).

### Nível 1 — A rota (fina e declarativa)

A rota só **declara** o que recebe e delega o trabalho. Exemplo, o APOD (`app/routers/apod.py`):

```python
router = APIRouter(prefix="/apod", tags=["APOD - Astronomy Picture of the Day"])
_URL = f"{settings.nasa_base_url}/planetary/apod"

@router.get("", summary="Imagem astronômica do dia")
async def get_apod(
    date: str | None = Query(None, description="Data YYYY-MM-DD..."),
    count: int | None = Query(None, description="Quantidade de imagens aleatórias."),
    thumbs: bool | None = Query(None, description="Retornar thumbnail de vídeos."),
) -> Any:
    return await fetch_json(_URL, {"date": date, "count": count, "thumbs": thumbs})
```

Três pontos para destacar:

- **`@router.get(...)`** — o *decorator* que diz "isso responde a HTTP GET".
- **`Query(None, ...)`** — declara **query parameters** (o que vem depois do `?` na URL).
  O `None` significa **opcional**. O FastAPI **valida tipos automaticamente**: se mandarem
  `count=abc`, ele já devolve erro **422** antes de chamar a NASA.
- **`async def`** — a função é **assíncrona** (explicado adiante).

### Tipos de parâmetro que aparecem no projeto

| Tipo | Como se declara | Exemplo de URL | Onde aparece |
|---|---|---|---|
| **Query opcional** | `Query(None, ...)` | `/apod?date=2024-01-01` | quase todos |
| **Query obrigatório** | `Query(..., ...)` | `/earth/imagery?lat=10&lon=20` | `earth.py` |
| **Path param** (parte da URL) | `Path(..., ...)` | `/neows/{asteroid_id}` | `neows.py` |
| **Validação com regras** | `Query(None, ge=1, le=100)` | `?size=50` (1 a 100) | `neows.py` |

O `...` (objeto *Ellipsis* do Python) é a forma do FastAPI dizer **"obrigatório"**.

### Nível 2 — O cliente HTTP (o motor que fala com a NASA)

Toda rota chama uma das três funções de `app/core/nasa_client.py`. A principal é
**`fetch_json`**. Fluxo passo a passo:

**Passo A — Um único cliente compartilhado (connection pooling).**
Em vez de abrir uma conexão nova a cada requisição (lento), o app cria **um**
`httpx.AsyncClient` no startup e o reusa para sempre. Isso é gerenciado pelo **`lifespan`**
em `main.py` — abre no boot, fecha no shutdown:

```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    await startup_client()   # cria o httpx.AsyncClient
    yield
    await shutdown_client()  # fecha no encerramento
```

**Passo B — Limpa os parâmetros vazios.**
Parâmetros opcionais que vieram `None` são **removidos** antes de chamar a NASA — para não
mandar `?date=&count=` vazios:

```python
def _clean_params(params):
    return {key: value for key, value in params.items() if value is not None}
```

**Passo C — Injeta a API key automaticamente.**
O front nunca manda a chave; o gateway a adiciona aqui:

```python
query.setdefault("api_key", settings.nasa_api_key)
```

**Passo D — Faz o GET, com retry em falhas temporárias.**
Algumas APIs da NASA "piscam" (caem por um instante, devolvem 502/503/504). O cliente
**tenta de novo** até 2 vezes, com um pequeno *backoff* (espera crescente). Isso
transforma a maioria das falhas momentâneas em sucesso.

**Passo E — Devolve o JSON** ou levanta um erro padronizado:

```python
async def fetch_json(url, params=None, *, with_api_key=True, headers=None):
    response = await _request(url, _build_query(params, with_api_key), headers)
    if response.status_code >= 400:
        _raise_for_status(response)      # vira NasaAPIError
    return response.json()
```

### As três variações de fetch — porque a NASA não devolve só JSON

Ponto rico para Web Services: **negociação de conteúdo** (*content negotiation*). Nem toda
API devolve JSON, então existem três funções:

| Função | Retorna | Usada quando a NASA devolve... | Exemplo |
|---|---|---|---|
| **`fetch_json`** | dict/list | **JSON** (a maioria) | APOD, NeoWs, EONET |
| **`fetch_bytes`** | bytes + content-type | **imagem binária** (PNG/JPG) | Earth (Landsat), tiles GIBS/Trek |
| **`fetch_text`** | texto + content-type | **XML** (catálogos WMTS) | GIBS `capabilities`, Trek |

Exemplo de **resposta binária** — o gateway recebe os bytes da imagem e os devolve com o
`media_type` correto (`app/routers/earth.py`):

```python
content, content_type = await fetch_bytes(f"{_BASE}/imagery", {"lat": lat, "lon": lon, ...})
return Response(content=content, media_type=content_type)   # devolve o PNG cru
```

### Os 4 padrões de GET do projeto (mostrar na apresentação)

1. **GET simples com query params** → APOD, NeoWs feed. Ex.: `/apod?date=...`
2. **GET com path param** (recurso identificado na URL) → `/neows/{asteroid_id}`,
   `/mars-rover/rovers/{rover}/photos`. É o estilo **REST**: a URL representa um *recurso*.
3. **GET que devolve binário** → `/earth/imagery`, `/gibs/tile/{z}/{x}/{y}` (imagens de mapa).
4. **GET com headers / sem chave** → o SSC precisa enviar `Accept: application/json` (senão
   a NASA responde XML); e vários serviços (GIBS, Trek, SSC) **não usam api_key** — por isso
   o parâmetro `with_api_key=False`.

---

## 5. Tratamento de erros — uniformidade

Cada API da NASA falha de um jeito. O gateway converte **tudo** num único formato
(`app/core/exceptions.py`):

```json
{ "error": true, "status_code": 429, "message": "Limite de requisições da NASA atingido..." }
```

Como funciona:

- Qualquer problema vira uma exceção `NasaAPIError` (timeout → 504, conexão falhou → 502,
  rate limit → 429...).
- Um **exception handler** registrado no `main.py` captura essa exceção e a transforma no
  JSON acima.
- Há ainda uma "rede de segurança": um handler genérico para `Exception` que evita
  **vazar stack trace** para o cliente — boa prática de segurança.

Assim, o front **sempre** sabe o que esperar quando dá erro.

| Situação | status_code devolvido |
|---|---|
| Tempo de resposta excedido | **504** (timeout) |
| Falha de conexão com a NASA | **502** (bad gateway) |
| Limite de requisições atingido | **429** (rate limit) |
| Erro da NASA `>= 500` | **502** (normalizado) |
| Erro inesperado no gateway | **500** (sem stack trace) |

---

## 6. Conceitos de "Web Services e APIs" que o projeto demonstra

Slide de amarração teórica — tudo isso aparece no código:

- **API REST / HTTP** — uso de métodos (só GET), URLs como recursos, **status codes**
  (200, 404, 429, 502, 504).
- **API Gateway / Proxy reverso** — um ponto único de entrada que orquestra 18 backends.
- **CORS** (*Cross-Origin Resource Sharing*) — configurado no `main.py`, permitindo apenas
  a origem do front e apenas o método GET.
- **Autenticação por API key** — injetada no servidor, escondida do cliente.
- **Negociação de conteúdo** — JSON × XML × binário (as três funções `fetch_*`).
- **Versionamento de API** — o prefixo `/api/v1`.
- **Programação assíncrona** (`async/await`) — enquanto espera a NASA responder, o servidor
  atende **outras** requisições. Crucial num gateway, onde quase todo o tempo é
  "esperando a rede".
- **Connection pooling** — reusar conexões TCP para ganho de performance.
- **Resiliência** — *retry* com *backoff* em falhas transitórias.
- **Documentação automática** (OpenAPI / Swagger) — gerada do próprio código em `/docs`.
- **12-Factor / config por ambiente** — segredos em `.env`, nunca no código.

---

## 7. Fluxo completo de uma requisição

Exemplo: usuário pede asteroides de uma semana.

```
1. Front:   GET http://localhost:8000/api/v1/neows/feed?start_date=2024-01-01&end_date=2024-01-07
2. FastAPI: casa o GET → router neows → função get_feed()
3. Valida:  start_date / end_date são strings? (FastAPI checa os tipos)
4. Rota:    chama fetch_json(".../neo/rest/v1/feed", {start_date, end_date})
5. Cliente: remove params None → injeta api_key → faz o GET na NASA (com retry)
6. NASA:    responde JSON com os asteroides
7. Cliente: se status >= 400 → vira NasaAPIError; senão devolve o JSON
8. Front:   recebe o JSON limpo (ou o erro padronizado)
```

E nada disso é armazenado — assim que a resposta sai, o gateway "esquece" tudo
(*stateless*).

---

## 8. Como rodar e testar

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
cp .env.example .env              # configurar NASA_API_KEY
uvicorn app.main:app --reload
```

- Swagger (docs interativa): <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Healthcheck: <http://127.0.0.1:8000/health>

Exemplos de consumo:

```bash
curl "http://127.0.0.1:8000/api/v1/apod"
curl "http://127.0.0.1:8000/api/v1/neows/feed?start_date=2024-01-01&end_date=2024-01-02"
curl "http://127.0.0.1:8000/api/v1/mars-rover/rovers/curiosity/photos?sol=1000&camera=NAVCAM"
curl "http://127.0.0.1:8000/api/v1/eonet/events?status=open&limit=5"
curl "http://127.0.0.1:8000/api/v1/gibs/layers"
curl "http://127.0.0.1:8000/api/v1/ssc/observatories"
```

Testes automatizados:

```bash
cd backend
pytest
```

---

> **Resumo de uma frase:** este backend é um *gateway* FastAPI assíncrono e *stateless* que
> expõe 64 endpoints GET sobre 18 APIs da NASA, escondendo a chave de API, padronizando
> erros e contornando CORS para que o front-end React consuma tudo a partir de uma única
> origem.
