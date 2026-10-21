export default function SourceList({ sources }) {
  if (!sources?.length) {
    return <p className="muted source-empty">No source references were returned.</p>
  }

  return (
    <details className="source-list">
      <summary>Sources <span>{sources.length}</span></summary>
      <ul>
        {sources.map((source) => (
          <li key={`${source.access_level}:${source.source}`}>
            <span className="source-icon" aria-hidden="true">↳</span>
            <span>
              <strong>{source.title}</strong>
              <small>{source.source} · {source.access_level}</small>
            </span>
          </li>
        ))}
      </ul>
      <p className="muted source-note">References come from authorized retrieval metadata. No file paths or hidden content are fetched.</p>
    </details>
  )
}
