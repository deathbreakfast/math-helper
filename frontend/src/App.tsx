import { useEffect, useState } from 'react'
import './App.css'

type HelloResponse = {
  message: string
}

function App() {
  const [hello, setHello] = useState<string>('Loading greeting...')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let didCancel = false

    const fetchGreeting = async () => {
      try {
        const response = await fetch('/api/hello')
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`)
        }
        const data: HelloResponse = await response.json()
        if (!didCancel) {
          setHello(data.message)
          setError(null)
        }
      } catch (err) {
        if (!didCancel) {
          setError(err instanceof Error ? err.message : 'Unknown error')
        }
      }
    }

    fetchGreeting()

    return () => {
      didCancel = true
    }
  }, [])

  return (
    <main className="app-shell">
      <header className="app-hero">
        <p className="eyebrow">Math Helper</p>
        <h1>Building confidence one problem at a time</h1>
        <p className="subtitle">
          This placeholder UI confirms the frontend ↔ backend connection. Future iterations
          will add levels, progress tracking, and problem generators.
        </p>
        <div className="status-card">
          <p className="status-label">API status:</p>
          {error ? (
            <p className="status-error">{error}</p>
          ) : (
            <p className="status-success">{hello}</p>
          )}
        </div>
      </header>
    </main>
  )
}

export default App
