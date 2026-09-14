import React from 'react'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import type { Notification } from '../types'

export default function Activity() {
  const { data, refresh } = useApi(() => api.notifications.list())
  const notifs: Notification[] = data?.notifications ?? []

  async function markRead(id: string) {
    await api.notifications.markRead(id)
    refresh()
  }

  const typeVariant = (t: string): 'accent' | 'success' | 'warning' | 'error' | 'neutral' => {
    if (t === 'success' || t === 'approved') return 'success'
    if (t === 'warning' || t === 'approval_needed') return 'warning'
    if (t === 'error') return 'error'
    return 'accent'
  }

  return (
    <div style={{ padding: 28 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 24, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>Activity</h2>
        <p style={{ color: 'var(--graphite)', fontSize: 14.5, margin: 0 }}>
          RAAHI only surfaces what actually matters.
        </p>
      </div>

      {notifs.length === 0 ? (
        <Card style={{ textAlign: 'center', padding: 56 }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>🔔</div>
          <p style={{ color: 'var(--graphite)', margin: 0 }}>Nothing to show yet. Activity will appear here as RAAHI works.</p>
        </Card>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {notifs.map(n => (
            <Card key={n.id} style={{ opacity: n.read ? 0.65 : 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 14, flexWrap: 'wrap' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                    {!n.read && <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent)', flexShrink: 0 }} />}
                    <b style={{ fontSize: 14.5 }}>{n.title}</b>
                    <Badge variant={typeVariant(n.type)}>{n.type}</Badge>
                  </div>
                  <p style={{ margin: 0, fontSize: 13.5, color: 'var(--graphite)' }}>{n.body}</p>
                  <div style={{ fontSize: 12, color: 'var(--graphite-2)', marginTop: 6 }}>
                    {new Date(n.created_at).toLocaleString()}
                  </div>
                </div>
                {!n.read && (
                  <button
                    onClick={() => markRead(n.id)}
                    style={{ fontSize: 12.5, color: 'var(--accent)', fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer', flexShrink: 0 }}
                  >
                    Mark read
                  </button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
