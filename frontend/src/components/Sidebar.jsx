import { CATALOG } from '../services/endpoints'

// Left navigation: lists every NASA service. Selecting one updates the
// active service in the parent App.
export default function Sidebar({ activeId, onSelect }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-rocket">🚀</span>
        <div>
          <h1>NASA Explorer</h1>
          <small>Gateway FastAPI</small>
        </div>
      </div>
      <nav>
        {CATALOG.map((service) => (
          <button
            key={service.id}
            className={`nav-item ${activeId === service.id ? 'active' : ''}`}
            onClick={() => onSelect(service.id)}
          >
            {service.name}
          </button>
        ))}
      </nav>
      <footer className="sidebar-footer">
        Todos os dados via{' '}
        <a href="https://api.nasa.gov/" target="_blank" rel="noreferrer">
          api.nasa.gov
        </a>
      </footer>
    </aside>
  )
}
