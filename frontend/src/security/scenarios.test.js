import { afterEach, describe, expect, it, vi } from 'vitest'
import { runSecurityScenario } from './scenarios.js'

afterEach(() => vi.restoreAllMocks())

function respond(status, payload) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('security scenario assertions', () => {
  it('passes an authentication denial only when the real status is 401', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(respond(401, { detail: 'denied' }))
    const result = await runSecurityScenario('missing-token', { preference: 'employee' })
    expect(result).toMatchObject({ status: 'passed', httpStatus: 401 })
  })

  it('fails an employee-view probe when the API returns the HR-only source', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(respond(200, {
      results: [{ source: 'people-operations-policy.md' }],
    }))
    const result = await runSecurityScenario('role-scope', {
      token: 'ephemeral-test-token',
      preference: 'employee',
    })
    expect(result).toMatchObject({ status: 'failed', httpStatus: 200 })
  })

  it('requires an HR policy result for the HR-view expectation', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(respond(200, { results: [] }))
    const result = await runSecurityScenario('role-scope', {
      token: 'ephemeral-test-token',
      preference: 'hr',
    })
    expect(result.status).toBe('failed')
  })

  it('marks model-dependent checks blocked on HTTP 503 instead of passed', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(respond(503, { detail: 'internal detail is not displayed' }))
    const result = await runSecurityScenario('answer-contract', {
      token: 'ephemeral-test-token',
      preference: 'employee',
    })
    expect(result).toMatchObject({ status: 'blocked', httpStatus: 503 })
    expect(result.evidence).not.toContain('internal detail')
  })
})
