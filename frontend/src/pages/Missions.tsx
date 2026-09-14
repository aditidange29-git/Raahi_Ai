import React, { useState } from 'react'
import { usePoll, useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import ProgressBar from '../components/ProgressBar'
import type { Mission, AgentEvent } from '../types'

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

const STEP_LABELS = [
  'Discover', 'Qualify', 'Documents', 'Prepare', 'Approve', 'Submit', 'Verify', 'Monitor',
]

function MissionDetail({ mission, onClose }: { mission: Mission; onClose: () => void }) {
  const { data: eventsData } = usePoll(
    () => api.missions.events(mission.id), 4000, [mission.id]
  )
  const events: AgentEvent[] = eventsData?.events ?? []

  return (
    <div style={{ animation: 'fadeIn .2s ease' }}>
      {/* Back */}
      <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--accent)', fontWeight: 600, fontSize: 14, cursor: 'pointer', marginBottom: 20 }}>
        ← Back to Missions
      </button>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 22, flexWrap: 'wrap', gap: 14 }}>
        <div>
          <h2 style={{ fontSize: 24, margin: '0 0 6px', fontFamily: 'Manrope,sans-serif' }}>{mission.title}</h2>
          <p style={{ margin: 0, fontSize: 14, color: 'var(--graphite)' }}>{mission.goal}</p>
        </div>
        <Badge variant={STATE_BADGE[mission.state] ?? 'neutral'} dot pulse={mission.state === 'WAITING_FOR_APPROVAL'}>
          {stateLabel(mission.state)}
        </Badge>
      </div>

      {/* Progress tracker */}
      <Card style={{ marginBottom: 20 }}>
        <div style={{ overflowX: 'auto', paddingBottom: 4 }}>
          <div style={{ display: 'flex', alignItems: 'center', minWidth: 640 }}>
            {STEP_LABELS.map((label, idx) => {
              const step = mission.steps[idx]
              const stepState = step?.state ?? 'pending'
              const circColor = stepState === 'done' ? 'var(--success)' : stepState === 'active' ? 'var(--accent)' : 'var(--bg-alt)'
              const circText = stepState === 'done' ? '#fff' : stepState === 'active' ? '#fff' : 'var(--graphite-2)'
              return (
                <React.Fragment key={label}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, flex: 1, position: 'relative', zIndex: 1 }}>
                    <div style={{
                      width: 22, height: 22, borderRadius: '50%', background: circColor,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 11, color: circText,
                      border: stepState === 'pending' ? '1.5px solid var(--border-2)' : 'none',
                    }}>
                      {stepState === 'done' ? '✓' : idx + 1}
                    </div>
                    <span style={{ fontSize: 11.5, color: 'var(--graphite)', textAlign: 'center', lineHeight: 1.2 }}>{label}</span>
                  </div>
                  {idx < STEP_LABELS.length - 1 && (
                    <div style={{ flex: 1, height: 1.5, background: stepState === 'done' ? 'rgba(60,122,86,0.4)' : 'var(--border-2)', marginBottom: 18 }} />
                  )}
                </React.Fragment>
              )
            })}
          </div>
        </div>
      </Card>

      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 20, alignItems: 'start' }}>
        {/* Stats */}
        <Card>
          <h3 style={{ margin: '0 0 16px', fontSize: 15, fontFamily: 'Manrope,sans-serif' }}>Mission Details</h3>
          {[
            ['Progress', `${mission.progress}%`],
            ['Eligibility', `${Math.round(mission.eligibility_score * 100)}%`],
            ['State', stateLabel(mission.state)],
            ['Started', new Date(mission.created_at).toLocaleDateString()],
            mission.confirmation_number ? ['Confirmation', mission.confirmation_number] : null,
          ].filter(Boolean).map(([k, v]: any) => (
            <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid var(--border)', fontSize: 13.5 }}>
              <span style={{ color: 'var(--graphite)' }}>{k}</span>
              <span style={{ fontWeight: 600 }}>{v}</span>
            </div>
          ))}
          <div style={{ marginTop: 16 }}>
            <ProgressBar value={mission.progress} />
          </div>
        </Card>

        {/* Activity feed */}
        <Card>
          <h3 style={{ margin: '0 0 14px', fontSize: 15, fontFamily: 'Manrope,sans-serif' }}>Activity Log</h3>
          <div style={{ maxHeight: 320, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 0 }}>
            {events.length === 0 ? (
              <p style={{ color: 'var(--graphite-2)', fontSize: 13 }}>No events yet. Agent will log steps here.</p>
            ) : (
              [...events].reverse().map(ev => (
                <div key={ev.id} style={{ display: 'flex', gap: 12, padding: '10px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ fontSize: 12, color: 'var(--graphite-2)', width: 44, flexShrink: 0, paddingTop: 1 }}>
                    {new Date(ev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <span style={{ fontSize: 13.5 }}>{ev.message}</span>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}

export default function Missions() {
  const { data, loading, refresh } = usePoll(() => api.missions.list(), 5000)
  const missions: Mission[] = data?.missions ?? []
  const [selected, setSelected] = useState<Mission | null>(null)

  if (selected) {
    // Re-fetch the selected mission to get latest state
    const live = missions.find(m => m.id === selected.id) ?? selected
    return (
      <div style={{ padding: 28 }}>
        <MissionDetail mission={live} onClose={() => setSelected(null)} />
      </div>
    )
  }

  return (
    <div style={{ padding: 28 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 24, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>Missions</h2>
        <p style={{ color: 'var(--graphite)', fontSize: 14.5, margin: 0 }}>
          Each mission is one end-to-end application RAAHI is handling for you.
        </p>
      </div>

      {loading && missions.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 60, color: 'var(--graphite-2)' }}>Loading…</div>
      ) : missions.length === 0 ? (
        <Card style={{ textAlign: 'center', padding: 48 }}>
          <p style={{ color: 'var(--graphite)', marginBottom: 0 }}>No missions yet. Discover an opportunity to get started.</p>
        </Card>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {missions.map(m => (
            <Card key={m.id} hover onClick={() => setSelected(m)} style={{ display: 'flex', alignItems: 'center', gap: 20, flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: 200 }}>
                <h4 style={{ margin: '0 0 4px', fontSize: 15.5, fontFamily: 'Manrope,sans-serif', fontWeight: 600 }}>{m.title}</h4>
                <div style={{ fontSize: 12.5, color: 'var(--graphite-2)' }}>
                  Started {new Date(m.created_at).toLocaleDateString()}
                </div>
              </div>
              <div style={{ width: 160 }}>
                <ProgressBar value={m.progress} />
                <div style={{ fontSize: 12, color: 'var(--graphite-2)', marginTop: 4 }}>{m.progress}%</div>
              </div>
              <Badge variant={STATE_BADGE[m.state] ?? 'neutral'} dot={m.state === 'WAITING_FOR_APPROVAL'} pulse={m.state === 'WAITING_FOR_APPROVAL'}>
                {stateLabel(m.state)}
              </Badge>
              <span style={{ color: 'var(--graphite-2)', fontSize: 18 }}>›</span>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
