import { useState } from 'react'

// Renders a form for a single endpoint based on its `fields` declaration and
// invokes onSubmit(params) when the user runs the query.
export default function EndpointForm({ endpoint, loading, onSubmit }) {
  const initial = Object.fromEntries(
    endpoint.fields.map((f) => [f.name, f.default ?? '']),
  )
  const [values, setValues] = useState(initial)

  const update = (name, value) => setValues((prev) => ({ ...prev, [name]: value }))

  const handleSubmit = (event) => {
    event.preventDefault()
    onSubmit(values)
  }

  return (
    <form className="endpoint-form" onSubmit={handleSubmit}>
      {endpoint.fields.length === 0 && (
        <p className="muted">Este endpoint não requer parâmetros.</p>
      )}
      <div className="fields">
        {endpoint.fields.map((field) => (
          <label key={field.name} className="field">
            <span>
              {field.label}
              {field.required && <em className="req"> *</em>}
            </span>
            <input
              type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : 'text'}
              value={values[field.name]}
              required={field.required}
              step={field.type === 'number' ? 'any' : undefined}
              onChange={(e) => update(field.name, e.target.value)}
            />
          </label>
        ))}
      </div>
      <button type="submit" className="run-btn" disabled={loading}>
        {loading ? 'Consultando…' : 'Consultar'}
      </button>
    </form>
  )
}
