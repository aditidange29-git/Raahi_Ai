import React from 'react'
import type { AgentStatus } from '../types'

interface Props {
  page: string
  onNav: (p: string) => void
  agentStatus?: AgentStatus
  notifCount?: number
}

const NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: '▦' },
  { id: 'discover',  label: 'Discover',  icon: '◎' },
  { id: 'missions',  label: 'Missions',  icon: '⚡' },
  { id: 'documents', label: 'Documents', icon: '📄' },
  { id: 'approvals', label: 'Approvals', icon: '✔' },
  { id: 'activity',  label: 'Activity',  icon: '≡' },
  { id: 'settings',  label: 'Settings',  icon: '⚙' },
]

const statusColor: Record<string, string> = {
  idle: 'var(--graphite-2)',
  running: 'var(--success)',
  waiting_approval: 'var(--warning)',
}

export default function Sidebar({ page, onNav, agentStatus, notifCount = 0 }: Props) {
  return (
    <aside style={{
      width: 'var(--sidebar-w)', flexShrink: 0,
      borderRight: '1px solid var(--border)',
      background: 'var(--surface)',
      display: 'flex', flexDirection: 'column',
      position: 'sticky', top: 0, height: '100vh',
    }}>
      {/* Logo */}
      <div style={{ padding: '22px 22px 18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9, fontFamily: 'Manrope,sans-serif', fontWeight: 800, fontSize: 19 }}>
          <div style={{
            width: 30, height: 30, borderRadius: 8, background: 'var(--accent)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#fff', fontSize: 13, fontWeight: 800, flexShrink: 0,
          }}>R</div>
          RAAHI
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '6px 12px', overflowY: 'auto' }}>
        {NAV.map(item => (
          <button
            key={item.id}
            onClick={() => onNav(item.id)}
            style={{
              display: 'flex', alignItems: 'center', gap: 11,
              width: '100%', padding: '9px 12px', borderRadius: 'var(--radius-sm)',
              fontSize: 14, fontWeight: page === item.id ? 600 : 500,
              color: page === item.id ? 'var(--accent)' : 'var(--graphite)',
              background: page === item.id ? 'var(--accent-soft)' : 'transparent',
              border: 'none', cursor: 'pointer', marginBottom: 2, textAlign: 'left',
              transition: 'background .15s, color .15s',
            }}
          >
            <span style={{ fontSize: 15 }}>{item.icon}</span>
            {item.label}
            {item.id === 'approvals' && notifCount > 0 && (
              <span style={{
                marginLeft: 'auto', background: 'var(--warning-soft)', color: 'var(--warning)',
                fontSize: 11, fontWeight: 700, padding: '1px 7px', borderRadius: 100,
              }}>{notifCount}</span>
            )}
          </button>
        ))}
      </nav>

      {/* Agent status pill */}
      <div style={{ padding: 14, borderTop: '1px solid var(--border)' }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 9, padding: '9px 10px',
          borderRadius: 'var(--radius-sm)', background: 'var(--bg-alt)',
          fontSize: 13, fontWeight: 600, marginBottom: 10,
        }}>
          <span style={{
            width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
            background: agentStatus ? statusColor[agentStatus.status] : 'var(--graphite-2)',
            animation: agentStatus?.status === 'running' ? 'pulse 1.8s ease-in-out infinite' : 'none',
          }} />
          Agent {agentStatus?.status ?? 'connecting…'}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px' }}>
          <div style={{
            width: 32, height: 32, borderRadius: '50%', background: 'var(--accent)',
            color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 12.5, fontWeight: 700, flexShrink: 0,
          }}>AD</div>
          <div>
            <div style={{ fontSize: 13.5, fontWeight: 600 }}>Aditi Dange</div>
            <div style={{ fontSize: 12, color: 'var(--graphite-2)' }}>Applicant</div>
          </div>
        </div>
      </div>
    </aside>
  )
}
