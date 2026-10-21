import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, normalizeAnswer, requestJson } from './client.js'

afterEach(() => vi.restoreAllMocks())

describe('requestJson', () => {
  it('sends the bearer token in the Authorization header and returns the HTTP response', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('{"results":[]}', { status: 200 }))
    const response = await requestJson('/documents/search?q=leave', { token: 'ephemeral-test-token' })

    expect(response).toEqual({ status: 200, data: { results: [] } })
    expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe('Bearer ephemeral-test-token')
    expect(fetchMock.mock.calls[0][0]).toBe('/api/documents/search?q=leave')
  })

  it('does not include a body or content type on a GET request', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('{"status":"ok"}', { status: 200 }))
    await requestJson('/health')
    expect(fetchMock.mock.calls[0][1].body).toBeUndefined()
    expect(fetchMock.mock.calls[0][1].headers['Content-Type']).toBeUndefined()
  })

  it('rejects malformed JSON without exposing response text', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('<script>secret</script>', { status: 200 }))
    await expect(requestJson('/health')).rejects.toMatchObject({
      name: 'ApiError', kind: 'invalid-response',
      message: 'The backend returned an invalid JSON response.',
    })
  })
})

describe('normalizeAnswer', () => {
  it('deduplicates valid server sources and ignores malformed metadata', () => {
    expect(normalizeAnswer({
      answer: '  Supported answer.  ',
      sources: [
        { title: 'Handbook', source: 'employee-handbook.md', access_level: 'employee', snippet: 'not rendered' },
        { title: 'Handbook', source: 'employee-handbook.md', access_level: 'employee' },
        { title: 'Invalid source', source: 4, access_level: 'employee' },
      ],
    })).toEqual({
      answer: 'Supported answer.',
      sources: [{ title: 'Handbook', source: 'employee-handbook.md', access_level: 'employee' }],
    })
  })

  it('rejects an incomplete answer payload', () => {
    expect(() => normalizeAnswer({ answer: 4, sources: [] })).toThrow(ApiError)
  })
})
