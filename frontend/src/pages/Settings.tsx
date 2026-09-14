import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import Card from '../components/Card'
import Badge from '../components/Badge'

export default function Settings() {
  const { data: statusData } = useApi(() => api.agent.status())
  const [autonomy, setAutonomy] = useState<'supervised' | 'autopilot'>('supervised')

  const toggles = [
    { name: 'Auto-discover opportunities', hint: 'RAAHI scans for new matches weekly', on: true },
    { name: 'Document expiry alerts', hint: 'Get notified when documents need renewal', on: true },
    { name: 'Deadline reminders', hint: '7-day and 1-day reminders for open opportunities', on: true },
    { name: 'Submission receipts', hint: 'Confirm every submission via notification', on: true },
  ]
  const [toggleState, setToggleState] = useState(toggles.map(t => t.on))

  return (
    <div style={{ padding: 28 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 24, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>Settings</h2>
        <p style={{ color: 'var(--graphite)', fontSize: 14.5, margin: 0 }}>Configure how RAAHI operates on your behalf.</p>
      </div>

      {/* Agent status */}
      {statusData && (
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 16, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>Agent Status</h3>
          <p style={{ fontSize: 13.5, color: 'var(--graphite)', margin: '0 0 16px' }}>Current runtime configuration.</p>
          {[
            ['Status', statusData.status],
            ['Active Missions', statusData.active_missions],
            ['Model Provider', statusData.model_provider],
            ['Version', statusData.version],
            ['Tools Available', statusData.tools_available?.length ?? 0],
          ].map(([k, v]) => (
            <div key={k as string} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '13px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ fontSize: 14, fontWeight: 500 }}>{k}</span>
              <span style={{ fontWeight: 600, fontSize: 14 }}>{String(v)}</span>
            </div>
          ))}
        </Card>
      )}

      {/* Autonomy mode */}
      <Card style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>Autonomy Mode</h3>
        <p style={{ fontSize: 13.5, color: 'var(--graphite)', margin: '0 0 16px' }}>How much RAAHI does without asking you.</p>
        {[
          { id: 'supervised', title: 'Supervised', desc: 'RAAHI prepares everything but pauses before each significant action.' },
          { id: 'autopilot', title: 'Autopilot', desc: 'RAAHI works end-to-end and only interrupts for approvals and final decisions.' },
        ].map(opt => (
          <div
            key={opt.id}
            onClick={() => setAutonomy(opt.id as any)}
            style={{
              display: 'flex', gap: 10, alignItems: 'flex-start',
              padding: '12px 14px', border: `1px solid ${autonomy === opt.id ? 'var(--accent)' : 'var(--border-2)'}`,
              borderRadius: 'var(--radius)', marginBottom: 8, cursor: 'pointer',
              background: autonomy === opt.id ? 'var(--accent-soft)' : 'var(--surface)',
              transition: 'border-color .15s, background .15s',
            }}
          >
            <div style={{
              width: 17, height: 17, borderRadius: '50%', flexShrink: 0, marginTop: 2,
              border: `1.5px solid ${autonomy === opt.id ? 'var(--accent)' : 'var(--border-2)'}`,
              background: autonomy === opt.id ? 'var(--accent)' : 'transparent',
              boxShadow: autonomy === opt.id ? 'inset 0 0 0 3px #fff' : 'none',
            }} />
            <div>
              <b style={{ fontSize: 14, display: 'block' }}>{opt.title}</b>
              <span style={{ fontSize: 12.5, color: 'var(--graphite-2)' }}>{opt.desc}</span>
            </div>
          </div>
        ))}
      </Card>

      {/* Notification toggles */}
      <Card>
        <h3 style={{ fontSize: 16, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>Notifications</h3>
        <p style={{ fontSize: 13.5, color: 'var(--graphite)', margin: '0 0 4px' }}>Control what RAAHI notifies you about.</p>
        {toggles.map((t, i) => (
          <div key={t.name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '13px 0', borderBottom: i < toggles.length - 1 ? '1px solid var(--border)' : 'none' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 500 }}>{t.name}</div>
              <div style={{ fontSize: 12, color: 'var(--graphite-2)', marginTop: 2 }}>{t.hint}</div>
            </div>
            <div
              onClick={() => setToggleState(prev => prev.map((v, j) => j === i ? !v : v))}
              style={{
                width: 40, height: 23, borderRadius: 100, flexShrink: 0, cursor: 'pointer',
                background: toggleState[i] ? 'var(--accent)' : 'var(--border-2)',
                position: 'relative', transition: 'background .18s',
              }}
            >
              <div style={{
                position: 'absolute', top: 2.5, left: toggleState[i] ? 19 : 3, width: 18, height: 18,
                borderRadius: '50%', background: '#fff',
                transition: 'left .18s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
              }} />
            </div>
          </div>
        ))}
      </Card>
    </div>
  )
}
