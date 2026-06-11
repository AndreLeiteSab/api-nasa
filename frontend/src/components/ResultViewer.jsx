// Renderiza o resultado de uma chamada de endpoint. Em vez de despejar o JSON
// cru, tenta apresentar os dados de forma amigável:
//   1. endpoints binários -> uma única imagem
//   2. texto/XML          -> um bloco de texto estilizado e truncado (ex.: XML WMTS)
//   3. imagens em geral    -> uma galeria de thumbnails
//   4. arrays de registros -> uma tabela HTML
//   5. objetos simples     -> um cartão resumo de chave/valor
// O JSON cru fica sempre disponível em um bloco recolhível como fallback.

const MAX_TEXT = 50_000 // limita o texto renderizado para XMLs enormes não travarem a UI
const MAX_ROWS = 200 // limita as linhas da tabela para manter o DOM leve
const MAX_COLS = 10 // limita as colunas da tabela para legibilidade

// --- auxiliares ------------------------------------------------------------

// Alguns serviços (Satellite Situation Center) retornam JSON "tipado" do Jackson,
// onde cada valor vem embrulhado como ["com.algum.ClassName", valor]. Desembrulha
// para os dados ficarem legíveis. Só na visão estruturada, nunca no JSON cru.
const CLASS_NAME = /^[a-zA-Z_$][\w$]*(\.[a-zA-Z_$][\w$]*)+$/
function unwrapTyped(node) {
  if (Array.isArray(node)) {
    if (node.length === 2 && typeof node[0] === 'string' && CLASS_NAME.test(node[0])) {
      return unwrapTyped(node[1])
    }
    return node.map(unwrapTyped)
  }
  if (node && typeof node === 'object') {
    return Object.fromEntries(Object.entries(node).map(([k, v]) => [k, unwrapTyped(v)]))
  }
  return node
}

const isPlainObject = (v) => v != null && typeof v === 'object' && !Array.isArray(v)
const isScalar = (v) => v == null || ['string', 'number', 'boolean'].includes(typeof v)

// Percorre o payload e retorna o maior array cujos elementos são registros
// (objetos simples). Lida com arrays no topo e contêineres aninhados (ex.: EONET
// `events`, arrays por data do NeoWs, OSDR `hits.hits`, Trek `response.docs`).
function findRecordArray(data) {
  let best = null
  const visit = (node) => {
    if (Array.isArray(node)) {
      const objects = node.filter(isPlainObject)
      if (objects.length && objects.length >= node.length / 2) {
        if (!best || objects.length > best.length) best = objects
      }
      node.forEach(visit)
    } else if (isPlainObject(node)) {
      Object.values(node).forEach(visit)
    }
  }
  visit(data)
  return best
}

// As APIs SSD/CNEOS respondem com { fields: [...], data: [[...], ...] }. Converte
// essa forma colunar em um array de objetos (linhas).
function fromFieldsData(data) {
  if (isPlainObject(data) && Array.isArray(data.fields) && Array.isArray(data.data)) {
    const cols = data.fields
    return data.data.slice(0, MAX_ROWS).map((row) =>
      Object.fromEntries(cols.map((c, i) => [c, row[i]])),
    )
  }
  return null
}

function pickColumns(rows) {
  const cols = []
  rows.slice(0, 50).forEach((row) => {
    Object.keys(row).forEach((k) => {
      if (!cols.includes(k)) cols.push(k)
    })
  })
  return cols.slice(0, MAX_COLS)
}

function cell(value) {
  if (isScalar(value)) return value == null ? '—' : String(value)
  if (Array.isArray(value)) return `[${value.length}]`
  return '{…}'
}

const IMAGE_EXT = /\.(jpg|jpeg|png|gif)$/i

// A biblioteca de mídia da NASA serve a mesma foto em vários tamanhos via o
// esquema de nomes `<base>~<tamanho>.<ext>` (ex.: o endpoint /images/asset).
// Agrupamos essas variantes em uma única entrada: a menor para exibir, a maior
// para o link.
const ASSET_VARIANT = /^(.*)~(thumb|small|medium|large|orig)\.(jpg|jpeg|png|gif)$/i
const SIZE_RANK = { thumb: 0, small: 1, medium: 2, large: 3, orig: 4 }

function collapseVariants(images) {
  const groups = new Map()
  const result = []
  for (const img of images) {
    const match = ASSET_VARIANT.exec(img.src)
    if (!match) {
      result.push(img)
      continue
    }
    const base = match[1]
    const rank = SIZE_RANK[match[2].toLowerCase()] ?? 0
    let group = groups.get(base)
    if (!group) {
      // Mantém uma referência em `result` e altera no lugar para preservar a ordem.
      group = { entry: { src: img.src, href: img.src }, lo: rank, hi: rank }
      groups.set(base, group)
      result.push(group.entry)
    }
    if (rank <= group.lo) {
      group.entry.src = img.src
      group.lo = rank
    }
    if (rank >= group.hi) {
      group.entry.href = img.src
      group.hi = rank
    }
  }
  return result
}

// Coleta as imagens exibíveis como pares { src, href }: `src` é o que a galeria
// renderiza (um thumbnail quando houver) e `href` é o alvo em resolução cheia
// para onde o thumbnail aponta. São iguais quando a fonte tem uma única URL.
function collectImages(data) {
  const images = []
  // Os hosts de imagem da NASA suportam https; forçamos para a galeria nunca
  // esbarrar no bloqueio de conteúdo misto quando o app é servido via https.
  const https = (u) => u.replace(/^http:\/\//i, 'https://')
  const add = (src, href = src) => {
    if (typeof src === 'string') images.push({ src: https(src), href: https(href) })
  }
  const visit = (node) => {
    if (!node || typeof node !== 'object') return
    if (Array.isArray(node)) {
      node.forEach(visit)
      return
    }
    // Registros do EPIC trazem links montados pelo gateway: thumbnail + PNG em resolução cheia.
    if (typeof node.image_url === 'string') add(node.image_url, node.image_url_hd || node.image_url)
    if (typeof node.img_src === 'string') add(node.img_src)
    if (node.media_type === 'image' && typeof node.url === 'string') add(node.url)
    if (typeof node.hdurl === 'string') add(node.hdurl)
    // href de imagem "pura" (itens /images/asset da biblioteca de mídia da NASA).
    if (typeof node.href === 'string' && IMAGE_EXT.test(node.href)) add(node.href)
    if (Array.isArray(node.links)) {
      node.links.forEach((l) => {
        if (l && typeof l.href === 'string' && IMAGE_EXT.test(l.href)) add(l.href)
      })
    }
    Object.values(node).forEach(visit)
  }
  visit(data)
  // Remove duplicatas pelo src renderizado, mantendo a primeira ocorrência.
  const seen = new Map()
  for (const img of collapseVariants(images)) {
    if (!seen.has(img.src)) seen.set(img.src, img)
  }
  return [...seen.values()].slice(0, 60)
}

// --- subcomponentes --------------------------------------------------------

function RecordTable({ rows }) {
  const columns = pickColumns(rows)
  const shown = rows.slice(0, MAX_ROWS)
  return (
    <div className="table-wrap">
      <div className="table-caption">
        {rows.length} registro{rows.length === 1 ? '' : 's'}
        {rows.length > MAX_ROWS && ` (exibindo ${MAX_ROWS})`}
      </div>
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {shown.map((row, i) => (
            <tr key={i}>
              {columns.map((c) => (
                <td key={c}>{cell(row[c])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function SummaryCard({ data }) {
  const entries = Object.entries(data).filter(([, v]) => isScalar(v))
  if (!entries.length) return null
  return (
    <dl className="summary-card">
      {entries.map(([k, v]) => (
        <div key={k} className="summary-row">
          <dt>{k}</dt>
          <dd>{v == null ? '—' : String(v)}</dd>
        </div>
      ))}
    </dl>
  )
}

// --- principal --------------------------------------------------------------

export default function ResultViewer({ result, error }) {
  if (error) {
    return (
      <div className="result error-box">
        <strong>Erro:</strong> {error}
      </div>
    )
  }
  if (result == null) {
    return <div className="result muted">Os resultados aparecerão aqui.</div>
  }

  // Endpoint binário (imagens/tiles) retorna um wrapper de URL de blob.
  if (result.__binary) {
    return (
      <div className="result">
        <img className="single-image" src={result.url} alt="Resultado da NASA" />
      </div>
    )
  }

  // Conteúdo de texto puro / XML (ex.: WMTS GetCapabilities).
  if (typeof result === 'string') {
    const truncated = result.length > MAX_TEXT
    return (
      <div className="result">
        <div className="table-caption">
          Texto ({(result.length / 1024).toFixed(1)} KB)
          {truncated && ` — exibindo os primeiros ${MAX_TEXT / 1000}k caracteres`}
        </div>
        <pre className="text-block">{result.slice(0, MAX_TEXT)}</pre>
      </div>
    )
  }

  const images = collectImages(result)
  const normalized = unwrapTyped(result)
  const rows = fromFieldsData(normalized) || findRecordArray(normalized)
  const summary = !rows && isPlainObject(normalized) ? normalized : null
  const json = JSON.stringify(result, null, 2)
  const hasFriendlyView = images.length > 0 || (rows && rows.length) || summary

  return (
    <div className="result">
      {images.length > 0 && (
        <div className="gallery">
          {images.map(({ src, href }) => (
            <a key={src} href={href} target="_blank" rel="noreferrer">
              <img src={src} alt="" loading="lazy" />
            </a>
          ))}
        </div>
      )}

      {rows && rows.length > 0 && <RecordTable rows={rows} />}
      {summary && <SummaryCard data={summary} />}

      <details open={!hasFriendlyView}>
        <summary>JSON bruto ({(json.length / 1024).toFixed(1)} KB)</summary>
        <pre className="json">{json}</pre>
      </details>
    </div>
  )
}
