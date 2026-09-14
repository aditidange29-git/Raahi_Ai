import React from 'react'
import { useApi, usePoll } from '../hooks/useApi'
import { api } from '../lib/api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import ProgressBar from '../components/ProgressBar'
import type { Mission, AgentStatus } from '../types'

interface Props { onNav: (p: string) => void }

const STATE_BADGE: Record<string, 'accent' | 'success' | 'warning' | 'error' | 'neutral'> = {
  DISCOVERING: 'accent', UNDERSTANDING: 'accent', CHECKING_ELIGIBILITY: 'accent',
  COLLECTING_DOCUMENTS: 'accent', PREPARING: 'accent',
  WAITING_FOR_APPROVAL: 'warning',
  EXECUTING: 'accent', VERIFYING: 'accent', MONITORING: 'accent',
  COMPLETED: 'success', BLOCKED: 'warning', FAILED: 'error', CANCELLED: 'neutral',
}

function stateLabel(s: string) {
  return s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export default function Dashboard({ onNav }: Props) {
  const { data: missionsData, refresh } = usePoll(() => api.missions.list(), 5000)
  const { data: agentData } = usePoll<AgentStatus>(() => api.agent.status(), 5000)
  const { data: notifData } = useApi(() => api.notifications.list())

  const missions: Mission[] = missionsData?.missions ?? []
  const activeMission = missions.find(m =>
    !['COMPLETED','FAILED','CANCELLED'].includes(m.state)
  )
  const completedCount = missions.filter(m => m.state === 'COMPLETED').length
  const pendingApproval = missions.filter(m => m.state === 'WAITING_FOR_APPROVAL').length

  return (
    <div style={{ padding: 28 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 24, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>
          Good morning, Aditi 👋
        </h2>
        <p style={{ color: 'var(--graphite)', fontSize: 14.5, margin: 0 }}>
          RAAHI is working in the background. Here's where things stand.
        </p>
      </div>

      {/* Active mission hero */}
      {activeMission && (
        <div style={{
          background: 'var(--accent)', color: '#fff', borderRadius: 'var(--radius-lg)',
          padding: '26px 28px', marginBottom: 22, position: 'relative', overflow: 'hidden',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5, fontWeight: 700, color: 'rgba(255,255,255,0.72)', marginBottom: 14 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#7CD9A0', animation: 'pulse 1.8s ease-in-out infinite', flexShrink: 0 }} />
            AGENT WORKING
          </div>
          <h3 style={{ fontSize: 21, margin: '0 0 4px', color: '#fff', fontFamily: 'Manrope,sans-serif' }}>
            {activeMission.title}
          </h3>
          <p style={{ color: 'rgba(255,255,255,0.75)', fontSize: 14, margin: '0 0 16px' }}>
            Current step: {stateLabel(activeMission.state)}
          </p>
          <ProgressBar
            value={activeMission.progress}
            color="#fff"
            height={6}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 }}>
            <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.75)' }}>{activeMission.progress}% complete</span>
            {activeMission.state === 'WAITING_FOR_APPROVAL' && (
              <button
                onClick={() => onNav('approvals')}
                style={{
                  background: '#fff', color: 'var(--accent)', border: 'none',
                  padding: '9px 18px', borderRadius: 'var(--radius-sm)',
                  fontSize: 14, fontWeight: 600, cursor: 'pointer',
                }}
              >
                Review &amp; Approve →
              </button>
            )}
          </div>
        </div>
      )}

      {/* Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 14, marginBottom: 28 }}>
        {[
          { num: missions.length, label: 'Total Missions' },
          { num: completedCount, label: 'Completed' },
          { num: pendingApproval, label: 'Awaiting Approval' },
          { num: notifData?.unread_count ?? 0, label: 'Unread Alerts' },
        ].map(m => (
          <Card key={m.label} style={{ padding: '18px 20px' }}>
            <div style={{ fontSize: 28, fontWeight: 800, fontFamily: 'Manrope,sans-serif', marginBottom: 2 }}>
              {m.num}
            </div>
            <div style={{ fontSize: 13, color: 'var(--graphite)' }}>{m.label}</div>
          </Card>
        ))}
      </div>

      {/* Recent missions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
        <h3 style={{ fontSize: 17, margin: 0, fontFamily: 'Manrope,sans-serif' }}>Active Missions</h3>
        <button onClick={() => onNav('missions')} style={{ fontSize: 13.5, color: 'var(--accent)', fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer' }}>
          View all →
        </button>
      </div>

      {missions.length === 0 ? (
        <Card style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>🎯</div>
          <p style={{ color: 'var(--graphite)', margin: '0 0 16px' }}>No missions yet. Discover an opportunity and let RAAHI handle it.</p>
          <button
            onClick={() => onNav('discover')}
            style={{
              background: 'var(--accent)', color: '#fff', border: 'none',
              padding: '10px 20px', borderRadius: 'var(--radius-sm)',
              fontSize: 14, fontWeight: 600, cursor: 'pointer',
            }}
          >
            Discover Opportunities
          </button>
        </Card>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 14 }}>
          {missions.slice(0, 6).map(m => (
            <Card key={m.id} hover onClick={() => onNav('missions')}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <h4 style={{ margin: 0, fontSize: 15.5, fontFamily: 'Manrope,sans-serif', fontWeight: 600, lineHeight: 1.3 }}>
                  {m.title}
                </h4>
                <Badge variant={STATE_BADGE[m.state] ?? 'neutral'}>
                  {stateLabel(m.state)}
                </Badge>
              </div>
              <ProgressBar value={m.progress} />
              <div style={{ marginTop: 10, fontSize: 12.5, color: 'var(--graphite-2)' }}>
                {m.progress}% · Updated {new Date(m.updated_at).toLocaleDateString()}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
