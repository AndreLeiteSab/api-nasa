import { useMemo, useState } from 'react'
import Sidebar from './components/Sidebar'
import EndpointForm from './components/EndpointForm'
import ResultViewer from './components/ResultViewer'
import { CATALOG } from './services/endpoints'
import { callEndpoint } from './services/api'

export default function App() {
  const [activeServiceId, setActiveServiceId] = useState(CATALOG[0].id)
  const [activeEndpointId, setActiveEndpointId] = useState(CATALOG[0].endpoints[0].id)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const service = useMemo(
    () => CATALOG.find((s) => s.id === activeServiceId),
    [activeServiceId],
  )
  const endpoint = useMemo(
    () => service.endpoints.find((e) => e.id === activeEndpointId) ?? service.endpoints[0],
    [service, activeEndpointId],
  )

  const selectService = (id) => {
    const next = CATALOG.find((s) => s.id === id)
    setActiveServiceId(id)
    setActiveEndpointId(next.endpoints[0].id)
    setResult(null)
    setError(null)
  }

  const selectEndpoint = (id) => {
    setActiveEndpointId(id)
    setResult(null)
    setError(null)
  }

  const runQuery = async (params) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await callEndpoint(endpoint.path, params, { binary: endpoint.binary })
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="layout">
      <Sidebar activeId={activeServiceId} onSelect={selectService} />
      <main className="content">
        <header className="content-header">
          <h2>{service.name}</h2>
          <p className="muted">{service.description}</p>
        </header>

        {service.endpoints.length > 1 && (
          <div className="endpoint-tabs">
            {service.endpoints.map((e) => (
              <button
                key={e.id}
                className={`tab ${endpoint.id === e.id ? 'active' : ''}`}
                onClick={() => selectEndpoint(e.id)}
              >
                {e.label}
              </button>
            ))}
          </div>
        )}

        <section className="panel">
          <EndpointForm
            key={endpoint.id}
            endpoint={endpoint}
            loading={loading}
            onSubmit={runQuery}
          />
        </section>

        <section className="panel results-panel">
          <ResultViewer result={result} error={error} />
        </section>
      </main>
    </div>
  )
}
