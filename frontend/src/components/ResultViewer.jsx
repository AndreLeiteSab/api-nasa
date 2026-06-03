// Renders the result of an endpoint call. Tries to surface images nicely
// (APOD, Mars photos, Earth imagery, NASA image library) and falls back to
// pretty-printed JSON for everything else.

function collectImages(data) {
  const images = []
  const visit = (node) => {
    if (!node || typeof node !== 'object') return
    if (Array.isArray(node)) {
      node.forEach(visit)
      return
    }
    // Common image-bearing shapes across NASA APIs.
    if (typeof node.img_src === 'string') images.push(node.img_src)
    if (node.media_type === 'image' && typeof node.url === 'string') images.push(node.url)
    if (typeof node.hdurl === 'string') images.push(node.hdurl)
    else if (node.media_type === 'image' && typeof node.url === 'string') {
      /* already handled */
    }
    if (Array.isArray(node.links)) {
      node.links.forEach((l) => {
        if (l && typeof l.href === 'string' && /\.(jpg|jpeg|png|gif)$/i.test(l.href)) {
          images.push(l.href)
        }
      })
    }
    Object.values(node).forEach(visit)
  }
  visit(data)
  // Dedupe and cap to keep the DOM light.
  return [...new Set(images)].slice(0, 60)
}

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

  // Binary endpoint (Earth imagery) returns a blob URL wrapper.
  if (result.__binary) {
    return (
      <div className="result">
        <img className="single-image" src={result.url} alt="Resultado da NASA" />
      </div>
    )
  }

  const images = collectImages(result)
  const json = JSON.stringify(result, null, 2)

  return (
    <div className="result">
      {images.length > 0 && (
        <div className="gallery">
          {images.map((src) => (
            <a key={src} href={src} target="_blank" rel="noreferrer">
              <img src={src} alt="" loading="lazy" />
            </a>
          ))}
        </div>
      )}
      <details open={images.length === 0}>
        <summary>JSON bruto ({(json.length / 1024).toFixed(1)} KB)</summary>
        <pre className="json">{json}</pre>
      </details>
    </div>
  )
}
