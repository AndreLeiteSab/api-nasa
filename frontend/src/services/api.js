// Thin client for the FastAPI gateway. All NASA traffic goes through it —
// the frontend never talks to api.nasa.gov directly.

const API_BASE = import.meta.env.VITE_API_BASE || ''
const PREFIX = '/api/v1'

/**
 * Build a query string from a params object, dropping empty values.
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
 * Resolve a path template like "/mars-rover/rovers/{rover}/photos" using the
 * provided params, returning the final path and the params not consumed by it.
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
 * Call a gateway endpoint. Returns parsed JSON, or for binary endpoints an
 * object describing the blob URL so the UI can render an image.
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
