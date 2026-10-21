import StatusBadge from './StatusBadge.jsx'

const pages = [
  { id: 'chat', label: 'Document chat', icon: '◈' },
  { id: 'security', label: 'Security lab', icon: '⌁' },
  { id: 'status', label: 'System status', icon: '◉' },
]

export default function AppShell({ page, onPageChange, rolePreference, onSignOut, children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#main" aria-label="RAGShield home">
          <span className="brand-mark">R</span>
          <span><strong>RAGShield</strong><small>LOCAL SECURITY LAB</small></span>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {pages.map((item) => (
            <button
              className={`nav-item ${page === item.id ? 'is-active' : ''}`}
              key={item.id}
              onClick={() => onPageChange(item.id)}
              aria-current={page === item.id ? 'page' : undefined}
            >
              <span aria-hidden="true">{item.icon}</span>{item.label}
              {item.id === 'security' && <span className="nav-tag">LAB</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="local-card">
            <span className="local-card-icon" aria-hidden="true">⌂</span>
            <div><strong>Local only</strong><small>Requests stay on this machine</small></div>
            <span className="online-indicator" aria-label="Local mode" />
          </div>
          <div className="profile-row">
            <span className="profile-avatar">{rolePreference === 'hr' ? 'H' : 'E'}</span>
            <span className="profile-copy"><strong>{rolePreference === 'hr' ? 'HR view' : 'Employee view'}</strong><small>Display preference only</small></span>
            <button className="icon-button signout-button" onClick={onSignOut} aria-label="Sign out" title="Sign out">↗</button>
          </div>
        </div>
      </aside>
      <main id="main" className="main-panel">
        <header className="topbar">
          <div className="breadcrumb"><span>RAGSHIELD</span><b>/</b><strong>{pages.find((item) => item.id === page)?.label}</strong></div>
          <div className="topbar-right"><StatusBadge status="local">Local environment</StatusBadge><span className="topbar-separator" /><span className="token-note">Token held in memory</span></div>
        </header>
        <div className="page-body">{children}</div>
      </main>
    </div>
  )
}
