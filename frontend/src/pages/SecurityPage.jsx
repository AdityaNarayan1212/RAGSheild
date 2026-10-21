import { useState } from 'react'
import StatusBadge from '../components/StatusBadge.jsx'
import { runSecurityScenario, securityScenarios } from '../security/scenarios.js'

export default function SecurityPage({ token, rolePreference, onAnswerAttempt }) {
  const [runs, setRuns] = useState({})
  const [running, setRunning] = useState('')

  async function run(scenario) {
    setRunning(scenario.id)
    setRuns((current) => ({ ...current, [scenario.id]: { status: 'running' } }))
    try {
      const result = await runSecurityScenario(scenario.id, { token, preference: rolePreference })
      if (scenario.model) {
        onAnswerAttempt({ httpStatus: result.httpStatus ?? null, kind: result.httpStatus ? undefined : 'network', at: new Date().toISOString() })
      }
      setRuns((current) => ({ ...current, [scenario.id]: result }))
    } catch (error) {
      if (scenario.model) onAnswerAttempt({ httpStatus: null, kind: 'network', at: new Date().toISOString() })
      setRuns((current) => ({ ...current, [scenario.id]: { status: 'failed', evidence: error.message } }))
    } finally {
      setRunning('')
    }
  }

  return (
    <section className="security-page">
      <div className="page-heading">
        <div><div className="eyebrow"><span className="eyebrow-line" /> CONTROLLED LOCAL PROBES</div><h1>Security lab</h1><p>Each run sends a real request to the local FastAPI application. Evidence appears only after the response arrives.</p></div>
        <StatusBadge status="local">Synthetic data only</StatusBadge>
      </div>
      <div className="security-notice"><span className="notice-icon" aria-hidden="true">⌁</span><div><strong>Read-only request checks</strong><p>These probes do not reindex Chroma or contact external systems. The HR indexing route is covered by backend tests because its POST operation rebuilds the persistent index.</p></div></div>
      <div className="security-context"><span>Assertion context</span><strong>{rolePreference === 'hr' ? 'HR view preference' : 'Employee view preference'}</strong><small>This label chooses expected results only; the backend token still controls access.</small></div>

      <div className="scenario-list">
        {securityScenarios.map((scenario) => {
          const runResult = runs[scenario.id]
          const isRunning = running === scenario.id
          return (
            <article className="scenario-card" key={scenario.id}>
              <div className="scenario-main">
                <div className="scenario-copy"><span className="scenario-category">{scenario.category}</span><h2>{scenario.name}</h2><p>{scenario.expected}</p></div>
                <div className="scenario-actions">
                  {scenario.model && <span className="model-tag">LOCAL MODEL</span>}
                  {runResult && <StatusBadge status={runResult.status}>{runResult.status === 'passed' ? 'Passed' : runResult.status === 'blocked' ? 'Blocked' : runResult.status === 'running' ? 'Running' : 'Failed'}</StatusBadge>}
                  <button className="button button--secondary" disabled={isRunning || (scenario.needsAuth && !token)} onClick={() => run(scenario)}>{isRunning ? 'Running…' : runResult ? 'Run again' : 'Run test'}</button>
                </div>
              </div>
              {runResult && runResult.status !== 'running' && <div className="scenario-evidence" aria-live="polite"><div><strong>{runResult.httpStatus ? `HTTP ${runResult.httpStatus}` : 'No HTTP response'}</strong><p>{runResult.evidence}</p>{runResult.sources?.length > 0 && <small>Returned source metadata: {runResult.sources.join(', ')}</small>}</div></div>}
              {scenario.needsAuth && !token && <p className="scenario-hint">Sign in with a locally configured token to run this check.</p>}
            </article>
          )
        })}
      </div>
      <div className="security-footnote"><strong>Test boundary</strong><p>The indirect-injection excerpt is kept in a separate synthetic fixture and is not injected into the production index. Prompt construction and role filtering are also checked by pytest; the live model cannot be proven safe by a refusal message.</p></div>
    </section>
  )
}
