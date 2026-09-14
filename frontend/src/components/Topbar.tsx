import React from 'react'

interface Props {
  title: string
  notifCount?: number
  onNotif?: () => void
}

export default function Topbar({ title, notifCount = 0, onNotif }: Props) {
  return (
    <header style={{
      height: 66, borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 28px', position: 'sticky', top: 0,
      background: 'rgba(250,248,243,0.92)', backdropFilter: 'blur(8px)', zIndex: 20,
    }}>
      <h1 style={{ fontSize: 19, margin: 0, fontFamily: 'Manrope,sans-serif', fontWeight: 700 }}>
        {title}
      </h1>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button
          onClick={onNotif}
          aria-label="Notifications"
          style={{
            width: 36, height: 36, borderRadius: '50%', border: 'none',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--graphite)', background: 'transparent', position: 'relative',
            cursor: 'pointer',
          }}
        >
          🔔
          {notifCount > 0 && (
            <span style={{
              position: 'absolute', top: 7, right: 8, width: 7, height: 7,
              background: 'var(--warning)', borderRadius: '50%',
              border: '1.5px solid var(--surface)',
            }} />
          )}
        </button>
      </div>
    </header>
  )
}
