import React from 'react'

type Variant = 'accent' | 'success' | 'warning' | 'error' | 'neutral'

const VARS: Record<Variant, { bg: string; color: string }> = {
  accent:  { bg: 'var(--accent-soft)',   color: 'var(--accent)' },
  success: { bg: 'var(--success-soft)',  color: 'var(--success)' },
  warning: { bg: 'var(--warning-soft)',  color: 'var(--warning)' },
  error:   { bg: 'var(--error-soft)',    color: 'var(--error)' },
  neutral: { bg: 'var(--bg-alt)',        color: 'var(--graphite)' },
}

interface Props {
  variant?: Variant
  dot?: boolean
  pulse?: boolean
  children: React.ReactNode
}

export default function Badge({ variant = 'neutral', dot, pulse, children }: Props) {
  const { bg, color } = VARS[variant]
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: '3px 10px', borderRadius: 100,
      fontSize: 12, fontWeight: 600,
      background: bg, color,
    }}>
      {dot && (
        <span style={{
          width: 7, height: 7, borderRadius: '50', flexShrink: 0,
          background: color,
          animation: pulse ? 'pulse 1.8s ease-in-out infinite' : 'none',
        }} />
      )}
      {children}
    </span>
  )
}
