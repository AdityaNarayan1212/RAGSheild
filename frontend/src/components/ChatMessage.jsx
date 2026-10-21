import SourceList from './SourceList.jsx'

export default function ChatMessage({ message }) {
  const isAssistant = message.role === 'assistant'
  return (
    <article className={`message message--${message.role}`}>
      <div className="message-avatar" aria-hidden="true">{isAssistant ? 'R' : 'Y'}</div>
      <div className="message-content">
        <div className="message-meta">
          <strong>{isAssistant ? 'RAGShield assistant' : 'You'}</strong>
          <span>{isAssistant ? 'Local answer' : 'Question'}</span>
        </div>
        <p className="message-text">{message.content}</p>
        {isAssistant && <SourceList sources={message.sources} />}
      </div>
    </article>
  )
}
