import { FormEvent, useEffect, useMemo, useState } from 'react'
import './App.css'

type HelloResponse = {
  message: string
}

type CreateUserResponse = {
  id: number
  avatar: string | null
  name: string
  pin: string
  share_url_params: {
    user: string
    pin: string
  }
}

const sanitizeAvatar = (avatar: string) => avatar.trim().slice(0, 4)

const sanitizeName = (name: string) => name.trim().slice(0, 64)

const sanitizePin = (pin: string) => pin.replace(/\D/g, '').slice(0, 4)

function App() {
  const [hello, setHello] = useState<string>('Loading greeting...')
  const [helloError, setHelloError] = useState<string | null>(null)

  const [avatar, setAvatar] = useState('')
  const [name, setName] = useState('')
  const [pin, setPin] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [shareLink, setShareLink] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const baseUrl = useMemo(() => {
    if (typeof window === 'undefined') {
      return ''
    }
    const { origin, pathname } = window.location
    return `${origin}${pathname}`.replace(/\/$/, '')
  }, [])

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
          setHelloError(null)
        }
      } catch (err) {
        if (!didCancel) {
          setHelloError(err instanceof Error ? err.message : 'Unknown error')
        }
      }
    }

    fetchGreeting()

    return () => {
      didCancel = true
    }
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') return
    const params = new URLSearchParams(window.location.search)
    const initialName = params.get('user')
    const initialPin = params.get('pin')
    if (initialName) setName(initialName)
    if (initialPin) setPin(initialPin)
  }, [])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFormError(null)
    setShareLink(null)

    const payload = {
      avatar: sanitizeAvatar(avatar),
      name: sanitizeName(name),
      pin: sanitizePin(pin),
    }

    setIsSubmitting(true)
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorBody = (await response.json()) as { errors?: string[] }
        throw new Error(errorBody.errors?.join(' ') || 'Failed to create user')
      }

      const data = (await response.json()) as CreateUserResponse
      const params = new URLSearchParams(data.share_url_params).toString()
      setShareLink(`${baseUrl}?${params}`)
      setAvatar('')
      setPin('')
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="app-hero">
        <p className="eyebrow">Math Helper</p>
        <h1>Building confidence one problem at a time</h1>
        <p className="subtitle">
          This placeholder UI now supports creating local-only learner accounts secured with a
          display name and 4-digit PIN shared via URL parameters.
        </p>
        <div className="status-card">
          <p className="status-label">API status:</p>
          {helloError ? (
            <p className="status-error">{helloError}</p>
          ) : (
            <p className="status-success">{hello}</p>
          )}
        </div>
      </header>

      <section className="status-card">
        <h2>Create a learner profile</h2>
        <p className="subtitle">
          Keep usage on a trusted network. PINs are stored in plain text to prioritize speed of
          setup during early prototyping.
        </p>

        <form className="create-user-form" onSubmit={handleSubmit}>
          <label>
            Avatar (emoji or short label)
            <input
              type="text"
              value={avatar}
              maxLength={4}
              onChange={(event) => setAvatar(event.target.value)}
              placeholder="🐯"
            />
          </label>

          <label>
            Display name
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Taylor"
              required
            />
          </label>

          <label>
            4-digit PIN
            <input
              type="password"
              value={pin}
              onChange={(event) => setPin(sanitizePin(event.target.value))}
              placeholder="1234"
              inputMode="numeric"
              pattern="\d{4}"
              required
            />
          </label>

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating…' : 'Create learner'}
          </button>
        </form>

        {formError && <p className="status-error">{formError}</p>}

        {shareLink && (
          <div className="share-link">
            <p className="status-label">Share this link (local network only):</p>
            <code>{shareLink}</code>
          </div>
        )}
      </section>
    </main>
  )
}

export default App
