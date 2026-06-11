# 🧪 Guia de Testes — NASA API Explorer

Valores **prontos e testados** para experimentar cada um dos 18 serviços, sem
precisar adivinhar parâmetros. Cada bloco diz **o que o endpoint retorna** e traz
**combos que funcionam**.

## Como testar

Existem 3 formas (da mais prática para a menos):

1. **Swagger** (recomendado para entender cada rota) — suba o backend e abra
   <http://127.0.0.1:8000/docs>. Cada endpoint tem **"Try it out"**, mostra os
   parâmetros e a resposta.
   ```bash
   cd backend && uvicorn app.main:app --reload
   ```
2. **Front-end** — `cd frontend && npm run dev` → <http://localhost:5173>.
   Escolha o serviço na barra lateral, preencha o formulário e clique
   **Consultar**. O resultado vira tabela / galeria / cartão automaticamente.
3. **curl / navegador** — todas as rotas ficam sob `http://127.0.0.1:8000/api/v1`.

> 🔑 **Chave de API.** Os serviços de `api.nasa.gov` (marcados com **🔑** abaixo)
> usam a `NASA_API_KEY` do `backend/.env`. O `DEMO_KEY` funciona, mas tem limite
> baixo (≈30 req/h) e, ao estourar, retorna `OVER_RATE_LIMIT`. Pegue uma chave
> grátis em <https://api.nasa.gov/> e coloque no `.env`. Os 9 serviços **sem 🔑**
> não dependem de chave.

## Mapa rápido dos 18 serviços

| Serviço | Precisa de chave? | Bom para testar com |
|---|:---:|---|
| APOD | 🔑 | `date=2024-01-01` |
| NeoWs | 🔑 | asteroide `3542519` |
| DONKI | 🔑 | maio/2024 (tempestade solar histórica) |
| EONET | — | `status=open`, `category=wildfires` |
| EPIC | 🔑 | `collection=natural` |
| Exoplanet | — | `where=disc_year>2020` |
| GIBS | — | tile `2/1/2` |
| InSight | 🔑 | (sem parâmetros — ver ressalva) |
| Image & Video Library | — | `q=moon` |
| OSDR | — | estudo `87` |
| Satellite Situation Center | — | (sem parâmetros) |
| SSD/CNEOS | — | `dist-max=0.05` |
| Techport | 🔑 | projeto `157166` |
| TechTransfer | 🔑 | `query=engine` |
| TLE | — | satélite `25544` (ISS) |
| Trek WMTS | — | `body=mars` |
| Earth *(bônus)* | 🔑 | `lat=29.78&lon=-95.33` *(instável)* |
| Mars Rover Photos *(bônus)* | 🔑 | `curiosity`, `sol=1000` |

---

## 1. APOD — Imagem astronômica do dia 🔑

Retorna **uma** imagem/vídeo com título, data, explicação e URL (`url` / `hdurl`).
Com `start_date`/`end_date` retorna uma **lista**; com `count`, imagens aleatórias.

| Caso | Parâmetros |
|---|---|
| Imagem de um dia | `date=2024-01-01` |
| Intervalo de datas | `start_date=2024-01-01` · `end_date=2024-01-05` |
| 3 aleatórias | `count=3` |

## 2. Asteroids NeoWs — Asteroides próximos 🔑

- **Feed por datas** (`/neows/feed`): asteroides que passam perto da Terra no
  período. Máx. **7 dias**. → `start_date=2024-01-01` · `end_date=2024-01-07`
- **Navegar** (`/neows/browse`): catálogo paginado. → `page=0` · `size=20`
- **Buscar por ID** (`/neows/{asteroid_id}`): detalhe de um asteroide. →
  `3542519` (testado ✅) ou `2000433` (Eros)

Cada asteroide traz diâmetro estimado, se é "potencialmente perigoso" e os dados
de aproximação (velocidade, distância).

## 3. DONKI — Clima espacial 🔑

Cada subrota é um tipo de evento solar e usa `start_date`/`end_date`.
**Dica:** use **maio/2024** — houve uma tempestade solar histórica, então quase
todas as subrotas têm dados nesse mês.

| Subrota | Parâmetros |
|---|---|
| CME, FLR, GST, SEP, IPS, HSS… | `start_date=2024-05-01` · `end_date=2024-05-31` |
| Notificações | `start_date=2024-05-01` · `end_date=2024-05-31` · `type=all` |

> Se uma subrota voltar lista vazia `[]`, é porque não houve aquele tipo de evento
> no período — troque a data, não é erro.
>
> ⚠️ O backend do DONKI na NASA **cai/sobrecarrega com frequência** e responde
> `503`/`timeout`. O gateway tenta de novo automaticamente (retry) e, se a NASA
> continuar fora, devolve um erro claro (`502`/`504`). Não é bug do projeto —
> espere alguns minutos e tente outra vez.

## 4. EONET — Eventos naturais da Terra

Rastreia furacões, incêndios, vulcões, enchentes etc. (veja também a explicação
detalhada que você já recebeu).

| Endpoint | Parâmetros |
|---|---|
| Eventos | `status=open` · `limit=10` |
| Vulcões ativos | `status=open` · `category=volcanoes` |
| Incêndios (60 dias) | `category=wildfires` · `days=60` |
| Categorias / Fontes / Camadas / Magnitudes | *(sem parâmetros)* |

Categorias válidas: `drought, dustHaze, earthquakes, floods, landslides, manmade,
seaLakeIce, severeStorms, snow, tempExtremes, volcanoes, waterColor, wildfires`.
⚠️ Em `coordinates` a ordem é **[longitude, latitude]**.

## 5. EPIC — Imagens da Terra inteira (DSCOVR) 🔑

| Endpoint | Parâmetros | Retorna |
|---|---|---|
| Mais recentes | `collection=natural` | metadados das últimas imagens |
| Datas disponíveis | `collection=natural` | lista de datas com imagem |
| Por data | `collection=natural` · `date=<uma data de "disponíveis">` | imagens daquele dia |

> Fluxo: chame **"Datas disponíveis"** primeiro, copie uma data da lista e use em
> **"Por data"**. Coleções: `natural` ou `enhanced`. Se vier lista vazia, a data
> não tem imagem — escolha outra de `/available`.

## 6. Exoplanet Archive — Exoplanetas

Consulta SQL-like ao arquivo. Use `select` (colunas), `where` (filtro) e `order`.

| Caso | Parâmetros |
|---|---|
| Planetas descobertos após 2020 | `table=exoplanets` · `select=pl_name,hostname,disc_year` · `where=disc_year>2020` |
| Planetas de período longo | `table=exoplanets` · `where=pl_orbper>300` |

> Se a tabela `exoplanets` falhar (é a API legada), tente `table=cumulative`
> (catálogo Kepler/KOI).

## 7. GIBS — Satélite em tiles (WMTS)

| Endpoint | Parâmetros | Retorna |
|---|---|---|
| Camadas (exemplos) | *(nenhum)* | lista pronta de camadas + coordenadas de exemplo |
| Tile (imagem) | `tile_matrix=2` · `tile_row=1` · `tile_col=2` · `layer=MODIS_Terra_CorrectedReflectance_TrueColor` · `date=2024-01-01` | uma imagem PNG/JPG |
| Catálogo WMTS (XML) | `epsg=epsg4326` | documento XML grande (exibido como texto) |

> Comece por **"Camadas"** para ver os identificadores e os zoom/linha/coluna de
> exemplo, depois use em **"Tile"**.

## 8. InSight — Clima em Marte 🔑

Sem parâmetros. **Ressalva honesta:** a missão InSight foi **encerrada em 2022**,
então a NASA costuma devolver poucos dados (ou só metadados antigos). É esperado
o resultado vir "magro" — não é bug do projeto.

## 9. NASA Image & Video Library — Mídia

| Endpoint | Parâmetros |
|---|---|
| Buscar | `q=moon` (ou `q=apollo 11`, `media_type=image`) |
| Assets de um item | `nasa_id=as11-40-5874` (testado ✅) |

A busca retorna `collection.items[]` — o front monta uma galeria automaticamente.

## 10. OSDR — Open Science Data Repository (biologia espacial)

| Endpoint | Parâmetros | Retorna |
|---|---|---|
| Buscar estudos | `term=space` · `size=10` | estudos (hits) |
| Metadados do estudo | `study_id=87` | documento completo do estudo |
| Arquivos do estudo | `study_ids=87` (ou `87,137`) | manifesto de arquivos |

## 11. Satellite Situation Center

| Endpoint | Parâmetros | Retorna |
|---|---|---|
| Observatórios / naves | *(nenhum)* | lista de espaçonaves rastreadas (ACE, etc.) |
| Estações terrestres | *(nenhum)* | estações terrestres |

> A resposta vem num JSON "tipado" (com nomes de classe Java). O front
> **desempacota** isso automaticamente e mostra uma tabela legível.

## 12. SSD/CNEOS (JPL) — Dinâmica do Sistema Solar

| Endpoint | Parâmetros | Retorna |
|---|---|---|
| Close Approach | `date-min=2024-01-01` · `date-max=2024-12-31` · `dist-max=0.05` | aproximações de NEOs |
| Fireballs | `limit=10` | bólidos atmosféricos |
| Sentry / Scout / NHATS | *(sem parâmetros)* | listas de risco / objetos / alvos |

> Estas rotas devolvem `{ fields, data }` (formato colunar). O front converte em
> tabela com os cabeçalhos certos.

## 13. Techport — Projetos de tecnologia 🔑

| Endpoint | Parâmetros | Retorna |
|---|---|---|
| Listar projetos | `updatedSince=2024-01-01` | IDs de projetos |
| Detalhe do projeto | `project_id=157166` (testado ✅) | título, datas, descrição, programa… |

> Fluxo: liste os IDs, copie um e use em **"Detalhe do projeto"**.

## 14. TechTransfer — Patentes, software e spinoffs 🔑

Todas as subrotas usam `query`. → `query=engine` (ou `solar`, `robot`, `medical`).
Subrotas: Patentes, Patentes emitidas, Software, Spinoff.

## 15. TLE — Órbitas de satélites

| Endpoint | Parâmetros | Retorna |
|---|---|---|
| Buscar | `search=iss` (ou `search=starlink`) | satélites pelo nome |
| Por NORAD ID | `satellite_number=25544` (ISS) | TLE de um satélite |

Outros IDs úteis: `20580` (Hubble), `43013` (NOAA-20).

## 16. Trek WMTS — Vesta / Lua / Marte

`body` aceita `moon`, `mars` ou `vesta`.

| Endpoint | Parâmetros | Retorna |
|---|---|---|
| Buscar itens | `body=mars` · `rows=5` | itens indexados (nomenclatura, produtos) |
| Tile do mosaico (imagem) | `body=moon` · `tile_matrix=0` · `tile_row=0` · `tile_col=0` | imagem do mosaico global |
| Catálogo WMTS (XML) | `body=moon` | documento XML (exibido como texto) |

## 17. Earth *(bônus)* 🔑

Imagem Landsat por coordenada. → `lat=29.78` · `lon=-95.33` · `date=2018-01-01`
· `dim=0.1`.

> ⚠️ **Serviço instável da própria NASA** — frequentemente dá timeout e o gateway
> responde `504 "Tempo de resposta da NASA excedido"`. Não é erro do projeto; o
> tratamento de erro está funcionando.

## 18. Mars Rover Photos *(bônus)* 🔑

| Endpoint | Parâmetros |
|---|---|
| Listar rovers | *(nenhum)* |
| Manifesto | `rover=curiosity` |
| Fotos | `rover=curiosity` · `sol=1000` · `camera=NAVCAM` |
| Fotos recentes | `rover=curiosity` |

Rovers: `curiosity`, `opportunity`, `spirit`, `perseverance`. Alternativa a `sol`:
`earth_date=2020-07-01`.

---

## Erros comuns (e o que significam)

| Mensagem | Causa | Solução |
|---|---|---|
| `429` / rate limit | `DEMO_KEY` estourou a cota (≈30 req/h) | Use chave própria no `.env` |
| `504 timeout` | A NASA demorou a responder (ex.: Earth, DONKI) | Tentar de novo — serviço instável |
| `502` / `503` | Backend da NASA fora do ar (DONKI, Earth) | Aguardar — o gateway já tenta retry sozinho |
| Lista vazia `[]` | Não há dados para aqueles parâmetros | Troque a data/filtro — não é erro |
| `403 / API_KEY_INVALID` | Chave ausente ou errada | Confira `NASA_API_KEY` no `.env` |
| `404` no Trek | `body` inválido | Use `moon`, `mars` ou `vesta` |

> O gateway **repete automaticamente** (até 2 vezes, com backoff) requisições que
> falham por conexão recusada ou erro `5xx` transitório — então boa parte das
> instabilidades da NASA é resolvida sozinha, sem o usuário perceber.
