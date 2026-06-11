import { CATALOG } from '../services/endpoints'

// Navegação lateral: lista todos os serviços da NASA. Selecionar um atualiza o
// serviço ativo no App pai.
export default function Sidebar({ activeId, onSelect }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <h1>NASA Explorer</h1>
        <small>Gateway FastAPI</small>
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
