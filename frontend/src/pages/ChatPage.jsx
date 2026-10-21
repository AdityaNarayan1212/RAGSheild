import { useState } from 'react'
import { ApiError, messageForStatus, normalizeAnswer, requestJson } from '../api/client.js'
import ChatMessage from '../components/ChatMessage.jsx'

const STARTER_QUESTIONS = [
  { icon: '↗', title: 'Time away', prompt: 'How do employees request leave?' },
  { icon: '◷', title: 'Workplace', prompt: 'What is the remote work policy?' },
  { icon: '⌕', title: 'Find a policy', prompt: 'Where can I find the employee handbook?' },
]

export default function ChatPage({ token, onAnswerAttempt }) {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function send(rawQuestion = question) {
    const query = rawQuestion.trim()
    if (!query || busy) return
    setQuestion('')
    setError('')
    setMessages((current) => [...current, { id: crypto.randomUUID(), role: 'user', content: query }])
    setBusy(true)
    try {
      const response = await requestJson('/documents/answer', {
        token,
        method: 'POST',
        body: { query },
      })
      onAnswerAttempt({ httpStatus: response.status, at: new Date().toISOString() })
      if (response.status !== 200) {
        throw new ApiError(messageForStatus(response.status), { status: response.status })
      }
      const answer = normalizeAnswer(response.data)
      setMessages((current) => [...current, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: answer.answer || 'The backend returned an empty answer.',
        sources: answer.sources,
      }])
    } catch (requestError) {
      setError(requestError.message || 'The answer request failed. Try again.')
      if (requestError instanceof ApiError && requestError.status === null) {
        onAnswerAttempt({ httpStatus: null, kind: requestError.kind, at: new Date().toISOString() })
      }
    } finally {
      setBusy(false)
    }
  }

  function onKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      send()
    }
  }

  return (
    <section className="chat-page">
      <div className="page-heading chat-heading">
        <div><div className="eyebrow"><span className="eyebrow-line" /> NOVATECH KNOWLEDGE BASE</div><h1>Ask your documents</h1><p>Answers use passages authorized by your backend token. The selected view is only a display preference.</p></div>
        <button className="button button--quiet" onClick={() => { setMessages([]); setError('') }} disabled={busy || (!messages.length && !error)}>↺ <span>Clear chat</span></button>
      </div>

      <div className={`chat-workspace ${messages.length ? 'has-messages' : ''}`}>
        {!messages.length ? (
          <div className="empty-state">
            <div className="empty-art" aria-hidden="true"><span className="art-ring art-ring--outer" /><span className="art-ring art-ring--inner" /><span className="art-center">R</span><i className="art-star art-star--one">✳</i><i className="art-star art-star--two">✦</i></div>
            <h2>A grounded answer starts with a source.</h2>
            <p>Ask about the local NovaTech documents. Retrieved references appear under each answer.</p>
            <div className="starter-grid">
              {STARTER_QUESTIONS.map((item) => <button key={item.title} className="starter-card" onClick={() => send(item.prompt)}><span>{item.icon}</span><strong>{item.title}</strong><small>{item.prompt}</small><b aria-hidden="true">↗</b></button>)}
            </div>
          </div>
        ) : (
          <div className="message-list" aria-live="polite">
            {messages.map((message) => <ChatMessage key={message.id} message={message} />)}
            {busy && <div className="typing-state" role="status"><span className="message-avatar">R</span><span className="typing-dots"><i /><i /><i /></span><span>Searching local sources…</span></div>}
          </div>
        )}
      </div>

      {error && <div className="chat-error" role="alert"><span aria-hidden="true">!</span><div><strong>Request could not be completed</strong><p>{error}</p></div><button className="icon-button" onClick={() => setError('')} aria-label="Dismiss error">×</button></div>}
      <form className="composer" onSubmit={(event) => { event.preventDefault(); send() }}>
        <label htmlFor="chat-question" className="sr-only">Ask a question about the local documents</label>
        <textarea id="chat-question" value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={onKeyDown} maxLength={200} rows={1} placeholder="Ask a question about your documents…" disabled={busy} />
        <div className="composer-footer"><span><span className="composer-lock" aria-hidden="true">⌑</span> Local model · retrieved passages only <span className="composer-count">{question.length}/200</span></span><button className="button button--primary send-button" disabled={busy || !question.trim()} type="submit">Send <span aria-hidden="true">↑</span></button></div>
      </form>
      <p className="chat-disclaimer">AI can make mistakes. Check the returned source references before relying on an answer.</p>
    </section>
  )
}
