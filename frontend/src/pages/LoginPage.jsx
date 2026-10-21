import { useState } from 'react'
import { messageForStatus, requestJson } from '../api/client.js'
import StatusBadge from '../components/StatusBadge.jsx'

export default function LoginPage({ onAuthenticated }) {
  const [token, setToken] = useState('')
  const [preference, setPreference] = useState('employee')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    if (!token.trim()) {
      setError('Enter a locally configured bearer token to continue.')
      return
    }
    setBusy(true)
    try {
      const response = await requestJson('/documents/search?q=leave', { token: token.trim() })
      if (response.status !== 200) {
        setError(messageForStatus(response.status))
        return
      }
      if (!Array.isArray(response.data?.results)) {
        setError('The backend response was incomplete. Check that the API is running the expected version.')
        return
      }
      onAuthenticated(token.trim(), preference)
      setToken('')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="login-screen">
      <section className="login-brand-panel">
        <a className="brand brand--login" href="#login">
          <span className="brand-mark">R</span>
          <span><strong>RAGShield</strong><small>LOCAL SECURITY LAB</small></span>
        </a>
        <div className="login-message">
          <div className="eyebrow"><span className="eyebrow-line" /> PRIVATE KNOWLEDGE, CONTROLLED ACCESS</div>
          <h1>Local knowledge.<br /><span>Clear boundaries.</span></h1>
          <p>A document assistant built to explore retrieval, authorization, and AI security on your own machine.</p>
          <div className="login-assurance"><span>⌂</span><span><strong>Nothing leaves your environment</strong><small>FastAPI, Ollama, and Chroma run locally.</small></span></div>
        </div>
        <div className="login-decoration" aria-hidden="true"><span /><span /><span /><i>R</i></div>
        <small className="login-footer">NOVATECH · SYNTHETIC DATASET · DEVELOPMENT USE</small>
      </section>
      <section className="login-form-panel" id="login">
        <div className="login-form-wrap">
          <StatusBadge status="unknown">Local API sign-in</StatusBadge>
          <h2>Welcome back</h2>
          <p className="login-lede">Use a token configured by the local backend administrator.</p>
          <form onSubmit={submit}>
            <label htmlFor="bearer-token">Bearer token</label>
            <input
              autoComplete="off"
              id="bearer-token"
              name="bearer-token"
              type="password"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              placeholder="Paste your local token"
              aria-describedby="token-help"
            />
            <small className="field-help" id="token-help">Held in memory for this session only. It is cleared when you sign out or refresh.</small>
            <label htmlFor="view-preference">Display preference</label>
            <select id="view-preference" value={preference} onChange={(event) => setPreference(event.target.value)}>
              <option value="employee">Employee view</option>
              <option value="hr">HR view</option>
            </select>
            <small className="field-help">This changes the interface label only. The backend token decides which data you can access.</small>
            {error && <p className="inline-error" role="alert">{error}</p>}
            <button className="button button--primary login-submit" disabled={busy} type="submit">
              {busy ? <><span className="spinner" /> Checking token…</> : <>Connect to local workspace <span aria-hidden="true">→</span></>}
            </button>
          </form>
          <div className="login-local-note"><span className="online-indicator" /> Local API · 127.0.0.1:8000</div>
        </div>
      </section>
    </main>
  )
}
