# 🚀 NASA API Explorer

Aplicação full-stack que permite consultar as **APIs abertas da NASA** através de
uma interface web amigável. O front-end (React + Vite) nunca acessa a NASA
diretamente: toda comunicação passa por um **gateway FastAPI** que intermedia,
trata erros e injeta a chave da API.

```
┌────────────┐      ┌─────────────────┐      ┌──────────────┐
│  Frontend  │ ───► │  Gateway FastAPI │ ───► │  APIs da NASA │
│ React+Vite │ ◄─── │   (este projeto) │ ◄─── │ api.nasa.gov  │
└────────────┘      └─────────────────┘      └──────────────┘
```

> O gateway é **stateless**: apenas repassa as respostas da NASA, sem armazenar dados.

## ✨ Funcionalidades

Cobre as **16 APIs GET** do portal <https://api.nasa.gov/> — cada uma com pelo
menos um exemplo de consumo no backend:

| # | Serviço (exigido) | Descrição |
|---|---|---|
| 1 | **APOD** | Imagem astronômica do dia |
| 2 | **Asteroids NeoWs** | Asteroides próximos (feed, browse, lookup) |
| 3 | **DONKI** | Clima espacial (CME, GST, FLR, SEP, IPS, MPC, RBE, HSS, WSA+Enlil, notificações) |
| 4 | **EONET** | Eventos naturais (events, categories, layers, sources, magnitudes) |
| 5 | **EPIC** | Imagens da Terra (natural/enhanced) |
| 6 | **Exoplanet Archive** | Consulta de exoplanetas |
| 7 | **GIBS** | Imagens de satélite em tiles WMTS (layers, tile, capabilities) |
| 8 | **InSight** | Clima em Marte |
| 9 | **Image & Video Library** | Busca de mídia (search, asset, metadata, captions, album) |
| 10 | **OSDR** | Open Science Data Repository — biologia espacial (search, meta, files) |
| 11 | **Satellite Situation Center** | Localização de naves/estações (observatories, ground-stations) |
| 12 | **SSD/CNEOS (JPL)** | Close approach, fireballs, sentry, scout, nhats |
| 13 | **Techport** | Projetos de tecnologia (lista e detalhe) |
| 14 | **TechTransfer** | Patentes, software e spinoffs |
| 15 | **TLE** | Órbitas de satélites |
| 16 | **Trek WMTS** | Mosaicos de Vesta/Lua/Marte (search, tile, capabilities) |

> O front-end **trata** as respostas: tabelas para listas de registros, cartões
> chave/valor para objetos, galeria para imagens e bloco de texto para XML — com
> o JSON bruto sempre disponível num bloco recolhível.

## 📁 Estrutura

```
api_nasa/
├── backend/            # API FastAPI (Python)
│   ├── app/
│   │   ├── config.py           # Configuração via .env
│   │   ├── main.py             # App + CORS + roteamento
│   │   ├── core/               # Cliente HTTP + tratamento de erros
│   │   └── routers/            # Um módulo por serviço da NASA
│   ├── tests/                  # Testes (offline, com mock)
│   └── requirements.txt
├── frontend/           # SPA React + Vite
│   └── src/
│       ├── services/   # Cliente da API + catálogo de endpoints
│       └── components/ # Sidebar, formulário e visualizador
└── README.md
```

## 🔧 Pré-requisitos

- **Python 3.11+**
- **Node.js 18+**
- Uma chave em <https://api.nasa.gov/> (opcional — `DEMO_KEY` funciona, mas com limite baixo)

## ▶️ Como rodar

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt

# Configure a chave (copie o exemplo e edite)
copy .env.example .env      # Windows
cp .env.example .env        # Linux/Mac
# edite .env e coloque sua NASA_API_KEY

uvicorn app.main:app --reload
```

Backend disponível em <http://127.0.0.1:8000> — docs interativas em
**<http://127.0.0.1:8000/docs>**.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend em <http://localhost:5173>. As chamadas `/api` são automaticamente
encaminhadas (proxy) para o backend.

## 🧪 Testes

```bash
cd backend
pytest
```

Os testes usam mock do cliente HTTP — rodam offline e não consomem a cota da NASA.

## 📚 Documentação da API

Toda a documentação dos endpoints é gerada automaticamente pelo FastAPI
(Swagger UI) em `/docs` e ReDoc em `/redoc`.

Para **testar cada serviço** com valores prontos (IDs reais, datas que funcionam),
veja o **[Guia de Testes](docs/GUIA-DE-TESTES.md)**.

## 🔒 Segurança

- A chave da NASA fica **apenas** no `.env` (nunca versionado).
- `.env` está no `.gitignore`; use `.env.example` como modelo.
- O backend valida e normaliza todos os erros antes de repassá-los.
"# api-nasa" 
