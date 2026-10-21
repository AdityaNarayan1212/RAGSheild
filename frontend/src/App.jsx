import { useState } from 'react'
import AppShell from './components/AppShell.jsx'
import ChatPage from './pages/ChatPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import SecurityPage from './pages/SecurityPage.jsx'
import StatusPage from './pages/StatusPage.jsx'

export default function App() {
  const [session, setSession] = useState(null)
  const [page, setPage] = useState('chat')
  const [lastAnswerAttempt, setLastAnswerAttempt] = useState(null)

  if (!session) return <LoginPage onAuthenticated={(token, preference) => setSession({ token, preference })} />

  function signOut() {
    setSession(null)
    setPage('chat')
    setLastAnswerAttempt(null)
  }

  return (
    <AppShell page={page} onPageChange={setPage} rolePreference={session.preference} onSignOut={signOut}>
      {page === 'chat' && <ChatPage token={session.token} onAnswerAttempt={setLastAnswerAttempt} />}
      {page === 'security' && <SecurityPage token={session.token} rolePreference={session.preference} onAnswerAttempt={setLastAnswerAttempt} />}
      {page === 'status' && <StatusPage lastAnswerAttempt={lastAnswerAttempt} />}
    </AppShell>
  )
}
