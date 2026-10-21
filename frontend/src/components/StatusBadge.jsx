export default function StatusBadge({ status = 'unknown', children }) {
  return (
    <span className={`status-badge status-badge--${status}`}>
      <span className="status-dot" aria-hidden="true" />
      {children}
    </span>
  )
}
