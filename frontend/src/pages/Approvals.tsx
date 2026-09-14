import React, { useState } from 'react'
import { usePoll } from '../hooks/useApi'
import { api } from '../lib/api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import ProgressBar from '../components/ProgressBar'
import type { Mission } from '../types'

export default function Approvals() {
  const { data, refresh } = usePoll(() => api.missions.list(), 4000)
  const missions: Mission[] = data?.missions ?? []
  const pending = missions.filter(m => m.state === 'WAITING_FOR_APPROVAL')
  const [resolving, setResolving] = useState<string | null>(null)
  const [resolved, setResolved] = useState<Record<string, 'approved' | 'denied'>>({})

  async function resolve(mission: Mission, action: 'approve' | 'deny') {
    setResolving(mission.id)
    try {
      await api.missions.approve(mission.id, action)
      setResolved(prev => ({ ...prev, [mission.id]: action }))
      setTimeout(refresh, 1500)
    } catch (e) {
      alert('Error: ' + (e instanceof Error ? e.message : e))
    } finally {
      setResolving(null)
    }
  }

  return (
    <div style={{ padding: 28 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 24, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>Approvals</h2>
        <p style={{ color: 'var(--graphite)', fontSize: 14.5, margin: 0 }}>
          RAAHI only surfaces what needs a real decision. Everything else happens automatically.
        </p>
      </div>

      {pending.length === 0 ? (
        <Card style={{ textAlign: 'center', padding: 56 }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>✅</div>
          <h3 style={{ margin: '0 0 8px', fontFamily: 'Manrope,sans-serif' }}>All clear</h3>
          <p style={{ color: 'var(--graphite)', margin: 0 }}>No approvals waiting. RAAHI is handling everything in the background.</p>
        </Card>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {pending.map(mission => {
            const alreadyResolved = resolved[mission.id]
            return (
              <Card key={mission.id}>
                {/* Warning banner */}
                <div style={{
                  background: 'var(--warning-soft)', border: '1px solid #EBD6AC',
                  borderRadius: 'var(--radius)', padding: '16px 18px', marginBottom: 20,
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 14, flexWrap: 'wrap',
                }}>
                  <div>
                    <b style={{ display: 'block', fontSize: 14.5 }}>⚠ Action Required: Application Submission</b>
                    <span style={{ fontSize: 13, color: 'var(--graphite)' }}>
                      RAAHI has prepared the application and needs your approval to submit.
                    </span>
                  </div>
                  <Badge variant="warning" dot pulse>Pending Approval</Badge>
                </div>

                {/* Mission info */}
                <h3 style={{ margin: '0 0 16px', fontFamily: 'Manrope,sans-serif', fontSize: 18 }}>
                  {mission.title}
                </h3>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 20 }}>
                  {[
                    ['Eligibility Score', `${Math.round(mission.eligibility_score * 100)}%`],
                    ['Progress', `${mission.progress}%`],
                    ['Current State', mission.state.replace(/_/g, ' ')],
                    ['Started', new Date(mission.created_at).toLocaleDateString()],
                  ].map(([k, v]) => (
                    <div key={k} style={{ background: 'var(--bg-alt)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
                      <div style={{ fontSize: 11.5, color: 'var(--graphite-2)', marginBottom: 3, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{k}</div>
                      <div style={{ fontSize: 14, fontWeight: 600 }}>{v}</div>
                    </div>
                  ))}
                </div>

                {/* Progress bar */}
                <div style={{ marginBottom: 20 }}>
                  <ProgressBar value={mission.progress} />
                </div>

                {/* Confirmation checklist */}
                <div style={{ marginBottom: 24 }}>
                  <p style={{ fontSize: 14, fontWeight: 600, margin: '0 0 12px' }}>By approving, you confirm:</p>
                  {[
                    'The application details are accurate and complete',
                    'All attached documents are valid and up to date',
                    'You authorize RAAHI to submit on your behalf',
                    'You understand this submission cannot be undone',
                  ].map(item => (
                    <div key={item} style={{ display: 'flex', gap: 9, alignItems: 'center', fontSize: 14, marginBottom: 8 }}>
                      <span style={{ color: 'var(--success)', fontWeight: 700 }}>✓</span>
                      {item}
                    </div>
                  ))}
                </div>

                {/* Action buttons */}
                {alreadyResolved ? (
                  <div style={{
                    padding: '14px 16px', borderRadius: 'var(--radius)',
                    background: alreadyResolved === 'approved' ? 'var(--success-soft)' : 'var(--error-soft)',
                    color: alreadyResolved === 'approved' ? 'var(--success)' : 'var(--error)',
                    fontWeight: 600, fontSize: 14,
                  }}>
                    {alreadyResolved === 'approved'
                      ? '✓ Approved — RAAHI is submitting your application…'
                      : '✗ Denied — Mission cancelled.'}
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <button
                      onClick={() => resolve(mission, 'approve')}
                      disabled={!!resolving}
                      style={{
                        width: '100%', padding: '12px 0',
                        background: 'var(--accent)', color: '#fff', border: 'none',
                        borderRadius: 'var(--radius-sm)', fontSize: 15, fontWeight: 600,
                        cursor: resolving ? 'wait' : 'pointer',
                      }}
                    >
                      {resolving === mission.id ? 'Processing…' : '✓ Approve & Submit Application'}
                    </button>
                    <div style={{ display: 'flex', gap: 10 }}>
                      <button
                        onClick={() => resolve(mission, 'deny')}
                        disabled={!!resolving}
                        style={{
                          flex: 1, padding: '10px 0',
                          background: 'transparent', color: 'var(--error)',
                          border: '1px solid var(--error-soft)', borderRadius: 'var(--radius-sm)',
                          fontSize: 14, fontWeight: 600, cursor: resolving ? 'wait' : 'pointer',
                        }}
                      >
                        ✗ Deny
                      </button>
                    </div>
                  </div>
                )}
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
