const API_PREFIX = '/api'
const REQUEST_TIMEOUT_MS = 180_000

export class ApiError extends Error {
  constructor(message, { status = null, kind = 'network' } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.kind = kind
  }
}

export function messageForStatus(status) {
  if (status === 401) return 'The backend rejected this bearer token. Sign in again.'
  if (status === 403) return 'This token is not authorized for that action.'
  if (status === 422) return 'The request did not meet the backend input requirements.'
  if (status === 503) return 'A required local backend service or token configuration is unavailable.'
  if (status >= 500) return 'The backend could not complete this request.'
  return 'The backend returned an unexpected response.'
}

export async function requestJson(path, { token, method = 'GET', body } = {}) {
  const headers = { Accept: 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  let response
  try {
    response = await fetch(`${API_PREFIX}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    })
  } catch (error) {
    const timedOut = error?.name === 'TimeoutError' || error?.name === 'AbortError'
    throw new ApiError(
      timedOut
        ? 'The request timed out. Check the local backend and try again.'
        : 'Cannot reach the local backend. Start FastAPI and try again.',
      { kind: timedOut ? 'timeout' : 'network' },
    )
  }

  let data
  try {
    const text = await response.text()
    data = text ? JSON.parse(text) : null
  } catch {
    throw new ApiError('The backend returned an invalid JSON response.', {
      status: response.status,
      kind: 'invalid-response',
    })
  }
  return { status: response.status, data }
}

export function normalizeAnswer(payload) {
  if (!payload || typeof payload !== 'object' || typeof payload.answer !== 'string') {
    throw new ApiError('The answer response was incomplete. Please try again.', {
      kind: 'invalid-response',
    })
  }

  const seen = new Set()
  const sources = Array.isArray(payload.sources)
    ? payload.sources.filter((source) => {
        if (
          !source ||
          typeof source.title !== 'string' ||
          typeof source.source !== 'string' ||
          typeof source.access_level !== 'string'
        ) return false
        const key = `${source.access_level}\u0000${source.source}`
        if (seen.has(key)) return false
        seen.add(key)
        return true
      }).map(({ title, source, access_level }) => ({ title, source, access_level }))
    : []

  return { answer: payload.answer.trim(), sources }
}
