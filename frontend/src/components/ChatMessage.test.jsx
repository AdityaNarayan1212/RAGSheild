import { describe, expect, it } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'
import ChatMessage from './ChatMessage.jsx'

describe('ChatMessage', () => {
  it('renders model content as escaped text and never as executable markup', () => {
    const markup = renderToStaticMarkup(<ChatMessage message={{
      role: 'assistant',
      content: '<img src=x onerror="alert(1)"><script>alert(2)</script>',
      sources: [],
    }} />)

    expect(markup).toContain('&lt;img')
    expect(markup).toContain('&lt;script&gt;')
    expect(markup).not.toContain('<script>')
    expect(markup).not.toContain('<img')
  })
})
