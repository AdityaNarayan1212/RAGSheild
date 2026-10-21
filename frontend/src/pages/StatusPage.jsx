import { useCallback, useEffect, useState } from 'react'
import { requestJson } from '../api/client.js'
import StatusBadge from '../components/StatusBadge.jsx'

export default function StatusPage({ lastAnswerAttempt }) {
  const [health, setHealth] = useState({ state: 'checking', checkedAt: null, error: '' })

  const refresh = useCallback(async () => {
    setHealth((current) => ({ ...current, state: 'checking', error: '' }))
    try {
      const response = await requestJson('/health')
      const healthy = response.status === 200 && response.data?.status === 'ok'
      setHealth({ state: healthy ? 'online' : 'unknown', checkedAt: new Date(), error: healthy ? '' : `Health endpoint returned HTTP ${response.status}.` })
    } catch (error) {
      setHealth({ state: 'offline', checkedAt: new Date(), error: error.message })
    }
  }, [])

  useEffect(() => { refresh() }, [refresh])

  return (
    <section className="status-page">
      <div className="page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> LOCAL RUNTIME</div><h1>System status</h1><p>Only supported health information is shown. This page does not run model inference.</p></div><button className="button button--secondary" onClick={refresh}>↻ Refresh status</button></div>
      <div className="status-grid">
        <article className="status-card"><div className="status-card-top"><span className="status-card-icon">⌘</span><StatusBadge status={health.state}>{health.state === 'online' ? 'Responding' : health.state === 'offline' ? 'Unavailable' : health.state === 'checking' ? 'Checking' : 'Unknown'}</StatusBadge></div><h2>FastAPI backend</h2><p>{health.state === 'online' ? 'GET /health returned HTTP 200.' : health.error || 'Waiting for the health response.'}</p><small>{health.checkedAt ? `Last checked ${health.checkedAt.toLocaleTimeString()}` : 'No check completed yet'}</small></article>
        <article className="status-card"><div className="status-card-top"><span className="status-card-icon">✳</span><StatusBadge status="unknown">Unknown</StatusBadge></div><h2>Ollama model readiness</h2><p>The health endpoint does not test the model. Readiness remains unknown until a real answer request succeeds.</p><small>No background inference has been started.</small></article>
        <article className="status-card"><div className="status-card-top"><span className="status-card-icon">▤</span><StatusBadge status="unknown">Unknown</StatusBadge></div><h2>Document index</h2><p>The API does not expose index status. The UI will not infer that indexing finished.</p><small>Indexing can be checked from the backend when appropriate.</small></article>
        <article className="status-card"><div className="status-card-top"><span className="status-card-icon">!</span><StatusBadge status={lastAnswerAttempt?.httpStatus === 503 ? 'warning' : lastAnswerAttempt?.httpStatus === 200 ? 'online' : 'unknown'}>{lastAnswerAttempt?.httpStatus === 503 ? 'HTTP 503 observed' : lastAnswerAttempt?.httpStatus === 200 ? 'HTTP 200 observed' : lastAnswerAttempt ? 'Request failed' : 'No answer request'}</StatusBadge></div><h2>Latest answer request</h2><p>{!lastAnswerAttempt ? 'No answer request has run in this session.' : lastAnswerAttempt.httpStatus === 503 ? `The last answer request returned HTTP 503 at ${new Date(lastAnswerAttempt.at).toLocaleTimeString()}. The exact dependency or token configuration issue is unknown.` : lastAnswerAttempt.httpStatus === 200 ? `The last answer request returned HTTP 200 at ${new Date(lastAnswerAttempt.at).toLocaleTimeString()}. This point-in-time result does not establish ongoing model readiness.` : `The last answer request failed (${lastAnswerAttempt.kind || `HTTP ${lastAnswerAttempt.httpStatus}`}).`}</p><small>Status only; no question or token is kept.</small></article>
      </div>
      <div className="status-caveat"><span>i</span><p><strong>Health is not readiness.</strong> A responding API does not establish that Ollama is running, models are installed, or the Chroma index is populated.</p></div>
    </section>
  )
}
