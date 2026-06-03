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

Cobre **todas as rotas GET** das APIs públicas da NASA:

| Serviço | Descrição |
|---|---|
| **APOD** | Imagem astronômica do dia |
| **NeoWs** | Asteroides próximos (feed, browse, lookup) |
| **DONKI** | Clima espacial (CME, GST, FLR, SEP, IPS, MPC, RBE, HSS, WSA+Enlil, notificações) |
| **Earth** | Imagens de satélite (imagery, assets) |
| **EONET** | Eventos naturais (events, categories, layers, sources, magnitudes) |
| **EPIC** | Imagens da Terra (natural/enhanced) |
| **Mars Rover Photos** | Fotos dos rovers (rovers, manifests, photos, latest) |
| **Image & Video Library** | Busca de mídia (search, asset, metadata, captions, album) |
| **TechTransfer** | Patentes, software e spinoffs |
| **InSight** | Clima em Marte |
| **Exoplanet Archive** | Consulta de exoplanetas |
| **TLE** | Órbitas de satélites |
| **SSD/CNEOS (JPL)** | Close approach, fireballs, sentry, scout, nhats |

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

## 🔒 Segurança

- A chave da NASA fica **apenas** no `.env` (nunca versionado).
- `.env` está no `.gitignore`; use `.env.example` como modelo.
- O backend valida e normaliza todos os erros antes de repassá-los.
"# api-nasa" 
