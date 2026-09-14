import React, { useState } from 'react'
import { usePoll } from './hooks/useApi'
import { api } from './lib/api'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import Dashboard from './pages/Dashboard'
import Discover from './pages/Discover'
import Missions from './pages/Missions'
import Documents from './pages/Documents'
import Approvals from './pages/Approvals'
import Activity from './pages/Activity'
import Settings from './pages/Settings'
import type { AgentStatus } from './types'

const PAGE_TITLES: Record<string, string> = {
  dashboard: 'Dashboard',
  discover: 'Discover Opportunities',
  missions: 'Missions',
  documents: 'Documents',
  approvals: 'Approvals',
  activity: 'Activity',
  settings: 'Settings',
}

export default function App() {
  const [page, setPage] = useState('dashboard')

  const { data: agentStatus } = usePoll<AgentStatus>(() => api.agent.status(), 5000)
  const { data: notifData } = usePoll(() => api.notifications.list(), 8000)

  const pendingApprovals = notifData?.notifications?.filter((n: any) => !n.read).length ?? 0

  function renderPage() {
    switch (page) {
      case 'dashboard':  return <Dashboard onNav={setPage} />
      case 'discover':   return <Discover onNav={setPage} />
      case 'missions':   return <Missions />
      case 'documents':  return <Documents />
      case 'approvals':  return <Approvals />
      case 'activity':   return <Activity />
      case 'settings':   return <Settings />
      default:           return <Dashboard onNav={setPage} />
    }
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar
        page={page}
        onNav={setPage}
        agentStatus={agentStatus ?? undefined}
        notifCount={pendingApprovals}
      />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        <Topbar
          title={PAGE_TITLES[page] ?? 'RAAHI'}
          notifCount={pendingApprovals}
          onNotif={() => setPage('activity')}
        />
        <main style={{ flex: 1, overflowY: 'auto' }}>
          {renderPage()}
        </main>
      </div>
    </div>
  )
}
