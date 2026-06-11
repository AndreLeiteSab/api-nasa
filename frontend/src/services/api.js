// Cliente fino do gateway FastAPI. Todo o tráfego da NASA passa por ele —
// o frontend nunca fala direto com api.nasa.gov.

const API_BASE = import.meta.env.VITE_API_BASE || ''
const PREFIX = '/api/v1'

/**
 * Monta uma query string a partir de um objeto de params, descartando valores vazios.
 */
function buildQuery(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      search.append(key, value)
    }
  })
  const qs = search.toString()
  return qs ? `?${qs}` : ''
}

/**
 * Resolve um template de caminho como "/epic/{collection}/date/{date}" usando os
 * params informados, retornando o caminho final e os params que não foram usados.
 */
function resolvePath(template, params) {
  const remaining = { ...params }
  const path = template.replace(/\{(\w+)\}/g, (_, name) => {
    const value = remaining[name] ?? ''
    delete remaining[name]
    return encodeURIComponent(value)
  })
  return { path, remaining }
}

/**
 * Chama um endpoint do gateway. Retorna o JSON já parseado ou, para endpoints
 * binários, um objeto descrevendo a URL do blob para a UI renderizar a imagem.
 */
export async function callEndpoint(template, params = {}, { binary = false } = {}) {
  const { path, remaining } = resolvePath(template, params)
  const url = `${API_BASE}${PREFIX}${path}${buildQuery(remaining)}`

  const response = await fetch(url)

  if (binary && response.ok) {
    const blob = await response.blob()
    return { __binary: true, url: URL.createObjectURL(blob), type: blob.type }
  }

  let data
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    data = await response.json()
  } else {
    data = await response.text()
  }

  if (!response.ok) {
    const message =
      (data && data.message) || `Erro ${response.status} ao consultar a NASA.`
    throw new Error(message)
  }
  return data
}
